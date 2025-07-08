"""
Cryptocurrency data providers with multiple free APIs.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

@dataclass
class CryptoPrice:
    """Cryptocurrency price data."""
    symbol: str
    exchange: str
    price: float
    volume: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None

class CryptoDataProvider:
    """Multi-source cryptocurrency data provider with arbitrage detection."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = None
        
        # Free API endpoints
        self.apis = {
            'coingecko': {
                'base_url': 'https://api.coingecko.com/api/v3',
                'rate_limit': 10,  # requests per minute
                'last_request': 0
            },
            'coinbase': {
                'base_url': 'https://api.exchange.coinbase.com',
                'rate_limit': 10,
                'last_request': 0
            },
            'binance': {
                'base_url': 'https://api.binance.com/api/v3',
                'rate_limit': 1200,  # requests per minute
                'last_request': 0
            },
            'kraken': {
                'base_url': 'https://api.kraken.com/0/public',
                'rate_limit': 1,  # requests per second
                'last_request': 0
            }
        }
        
        # Common cryptocurrency pairs for arbitrage
        self.major_pairs = [
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'ADA/USD',
            'SOL/USD', 'XRP/USD', 'DOT/USD', 'LINK/USD'
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_coingecko_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from CoinGecko API."""
        try:
            # Convert symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'ADA': 'cardano', 'SOL': 'solana', 'XRP': 'ripple',
                'DOT': 'polkadot', 'LINK': 'chainlink'
            }
            
            ids = [symbol_map.get(s.replace('/USD', ''), s.lower()) for s in symbols]
            ids_str = ','.join(ids)
            
            url = f"{self.apis['coingecko']['base_url']}/simple/price"
            params = {
                'ids': ids_str,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                prices = []
                for coin_id, price_data in data.items():
                    if 'usd' in price_data:
                        prices.append(CryptoPrice(
                            symbol=coin_id.upper(),
                            exchange='coingecko',
                            price=price_data['usd'],
                            volume=price_data.get('usd_24h_vol', 0),
                            timestamp=datetime.fromtimestamp(price_data.get('last_updated_at', 0))
                        ))
                
                return prices
                
        except Exception as e:
            self.logger.error(f"Error fetching CoinGecko prices: {e}")
            return []
    
    async def get_binance_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from Binance API."""
        try:
            # Convert symbols to Binance format
            binance_symbols = [s.replace('/', '').replace('USD', 'USDT') for s in symbols]
            
            url = f"{self.apis['binance']['base_url']}/ticker/24hr"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                prices = []
                for item in data:
                    symbol = item['symbol']
                    if symbol.endswith('USDT') and symbol.replace('USDT', '') in [s.replace('USDT', '') for s in binance_symbols]:
                        prices.append(CryptoPrice(
                            symbol=symbol.replace('USDT', '/USD'),
                            exchange='binance',
                            price=float(item['lastPrice']),
                            volume=float(item['volume']),
                            timestamp=datetime.fromtimestamp(int(item['closeTime']) / 1000),
                            bid=float(item['bidPrice']),
                            ask=float(item['askPrice'])
                        ))
                
                return prices
                
        except Exception as e:
            self.logger.error(f"Error fetching Binance prices: {e}")
            return []
    
    async def get_coinbase_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from Coinbase API."""
        try:
            prices = []
            
            for symbol in symbols:
                # Convert to Coinbase format
                cb_symbol = symbol.replace('/', '-')
                url = f"{self.apis['coinbase']['base_url']}/products/{cb_symbol}/ticker"
                
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            prices.append(CryptoPrice(
                                symbol=symbol,
                                exchange='coinbase',
                                price=float(data['price']),
                                volume=float(data['volume']),
                                timestamp=datetime.fromisoformat(data['time'].replace('Z', '+00:00')),
                                bid=float(data['bid']),
                                ask=float(data['ask'])
                            ))
                except Exception as e:
                    self.logger.warning(f"Error fetching {symbol} from Coinbase: {e}")
                    continue
            
            return prices
            
        except Exception as e:
            self.logger.error(f"Error fetching Coinbase prices: {e}")
            return []
    
    async def get_all_prices(self, symbols: Optional[List[str]] = None) -> Dict[str, List[CryptoPrice]]:
        """Get prices from all exchanges for comparison."""
        if symbols is None:
            symbols = self.major_pairs
        
        tasks = [
            self.get_coingecko_prices(symbols),
            self.get_binance_prices(symbols),
            self.get_coinbase_prices(symbols)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_prices = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Error in task {i}: {result}")
                continue
            
            for price in result:
                if price.symbol not in all_prices:
                    all_prices[price.symbol] = []
                all_prices[price.symbol].append(price)
        
        return all_prices
    
    def detect_arbitrage_opportunities(self, prices: Dict[str, List[CryptoPrice]], 
                                     min_profit_threshold: float = 0.005) -> List[Dict]:
        """Detect arbitrage opportunities between exchanges."""
        opportunities = []
        
        for symbol, price_list in prices.items():
            if len(price_list) < 2:
                continue
            
            # Sort by price
            sorted_prices = sorted(price_list, key=lambda x: x.price)
            lowest = sorted_prices[0]
            highest = sorted_prices[-1]
            
            # Calculate potential profit
            profit_percentage = (highest.price - lowest.price) / lowest.price
            
            if profit_percentage >= min_profit_threshold:
                opportunities.append({
                    'symbol': symbol,
                    'buy_exchange': lowest.exchange,
                    'sell_exchange': highest.exchange,
                    'buy_price': lowest.price,
                    'sell_price': highest.price,
                    'profit_percentage': profit_percentage,
                    'profit_amount': highest.price - lowest.price,
                    'timestamp': datetime.now(),
                    'confidence': self._calculate_confidence(lowest, highest)
                })
        
        return sorted(opportunities, key=lambda x: x['profit_percentage'], reverse=True)
    
    def _calculate_confidence(self, buy_price: CryptoPrice, sell_price: CryptoPrice) -> float:
        """Calculate confidence score for arbitrage opportunity."""
        confidence = 0.5  # Base confidence
        
        # Higher volume increases confidence
        if buy_price.volume > 1000000:  # $1M+ volume
            confidence += 0.2
        if sell_price.volume > 1000000:
            confidence += 0.2
        
        # Recent data increases confidence
        now = datetime.now()
        if (now - buy_price.timestamp).seconds < 300:  # Within 5 minutes
            confidence += 0.1
        if (now - sell_price.timestamp).seconds < 300:
            confidence += 0.1
        
        return min(confidence, 1.0)

async def main():
    """Test the crypto data provider."""
    logging.basicConfig(level=logging.INFO)
    
    async with CryptoDataProvider() as provider:
        print("🔍 Fetching crypto prices...")
        prices = await provider.get_all_prices()
        
        print(f"📊 Found prices for {len(prices)} symbols")
        for symbol, price_list in prices.items():
            print(f"  {symbol}: {len(price_list)} exchanges")
        
        print("\n💰 Detecting arbitrage opportunities...")
        opportunities = provider.detect_arbitrage_opportunities(prices)
        
        if opportunities:
            print(f"🎯 Found {len(opportunities)} opportunities:")
            for opp in opportunities[:5]:  # Show top 5
                print(f"  {opp['symbol']}: {opp['profit_percentage']:.2%} profit")
                print(f"    Buy on {opp['buy_exchange']} at ${opp['buy_price']:.2f}")
                print(f"    Sell on {opp['sell_exchange']} at ${opp['sell_price']:.2f}")
                print(f"    Confidence: {opp['confidence']:.2f}")
                print()
        else:
            print("❌ No arbitrage opportunities found")

if __name__ == "__main__":
    asyncio.run(main())