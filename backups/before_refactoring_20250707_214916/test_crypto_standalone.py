#!/usr/bin/env python3
"""
Standalone crypto arbitrage test - completely independent.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
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

class StandaloneCryptoProvider:
    """Standalone crypto data provider for testing."""
    
    def __init__(self):
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_coingecko_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from CoinGecko API."""
        try:
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'ADA': 'cardano', 'SOL': 'solana', 'XRP': 'ripple'
            }
            
            ids = [symbol_map.get(s.replace('/USD', ''), s.lower()) for s in symbols]
            ids_str = ','.join(ids)
            
            url = "https://api.coingecko.com/api/v3/simple/price"
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
            url = "https://api.binance.com/api/v3/ticker/24hr"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                target_symbols = [s.replace('/', '').replace('USD', 'USDT') for s in symbols]
                
                prices = []
                for item in data:
                    symbol = item['symbol']
                    if symbol in target_symbols:
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
                cb_symbol = symbol.replace('/', '-')
                url = f"https://api.exchange.coinbase.com/products/{cb_symbol}/ticker"
                
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
    
    async def get_all_prices(self, symbols: List[str]) -> Dict[str, List[CryptoPrice]]:
        """Get prices from all exchanges."""
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
        """Detect arbitrage opportunities."""
        opportunities = []
        
        for symbol, price_list in prices.items():
            if len(price_list) < 2:
                continue
            
            sorted_prices = sorted(price_list, key=lambda x: x.price)
            lowest = sorted_prices[0]
            highest = sorted_prices[-1]
            
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
        """Calculate confidence score."""
        confidence = 0.5
        
        if buy_price.volume > 1000000:
            confidence += 0.2
        if sell_price.volume > 1000000:
            confidence += 0.2
        
        now = datetime.now()
        if (now - buy_price.timestamp).seconds < 300:
            confidence += 0.1
        if (now - sell_price.timestamp).seconds < 300:
            confidence += 0.1
        
        return min(confidence, 1.0)

async def test_crypto_arbitrage():
    """Test crypto arbitrage detection."""
    print("🚀 STANDALONE CRYPTO ARBITRAGE TEST")
    print("=" * 50)
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        async with StandaloneCryptoProvider() as provider:
            print("✅ Provider initialized")
            
            # Test major cryptocurrencies
            symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD', 'ADA/USD', 'SOL/USD']
            print(f"🔍 Fetching prices for: {', '.join(symbols)}")
            
            prices = await provider.get_all_prices(symbols)
            
            print(f"\n📊 MARKET DATA:")
            print("-" * 30)
            
            total_exchanges = 0
            for symbol, price_list in prices.items():
                print(f"{symbol}:")
                for price in price_list:
                    print(f"  {price.exchange}: ${price.price:,.2f} (Vol: ${price.volume:,.0f})")
                    total_exchanges += 1
                print()
            
            print(f"📈 Total data points: {total_exchanges}")
            
            # Detect arbitrage opportunities
            print("\n💰 ARBITRAGE OPPORTUNITIES:")
            print("-" * 40)
            
            opportunities = provider.detect_arbitrage_opportunities(prices, 0.001)  # 0.1% threshold
            
            if opportunities:
                print(f"🎯 Found {len(opportunities)} opportunities:")
                
                for i, opp in enumerate(opportunities, 1):
                    print(f"\n🏆 OPPORTUNITY #{i}")
                    print(f"Symbol: {opp['symbol']}")
                    print(f"Profit: {opp['profit_percentage']:.3%}")
                    print(f"Buy: {opp['buy_exchange']} @ ${opp['buy_price']:,.2f}")
                    print(f"Sell: {opp['sell_exchange']} @ ${opp['sell_price']:,.2f}")
                    print(f"Profit per unit: ${opp['profit_amount']:,.2f}")
                    print(f"Confidence: {opp['confidence']:.2f}")
                    
                    # Calculate potential returns
                    investments = [100, 1000, 10000]
                    print("Potential returns:")
                    for amount in investments:
                        units = amount / opp['buy_price']
                        profit = units * opp['profit_amount']
                        roi = (profit / amount) * 100
                        print(f"  ${amount:,} → ${profit:.2f} profit ({roi:.2f}% ROI)")
                
                # Show best opportunity
                best = opportunities[0]
                print(f"\n🚨 BEST OPPORTUNITY:")
                print(f"🎯 {best['symbol']}: {best['profit_percentage']:.3%} profit")
                print(f"💰 ${best['profit_amount']:.2f} profit per unit")
                print(f"⚡ {best['buy_exchange']} → {best['sell_exchange']}")
                
            else:
                print("❌ No arbitrage opportunities found")
                print("💡 Try lowering the profit threshold or checking during high volatility")
            
            # Market summary
            print(f"\n📊 MARKET SUMMARY:")
            print("-" * 30)
            
            for symbol, price_list in prices.items():
                if price_list:
                    prices_only = [p.price for p in price_list]
                    min_price = min(prices_only)
                    max_price = max(prices_only)
                    spread = (max_price - min_price) / min_price * 100
                    
                    print(f"{symbol}: ${min_price:,.2f} - ${max_price:,.2f} (Spread: {spread:.2f}%)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def continuous_monitoring():
    """Run continuous monitoring."""
    print("\n🔄 CONTINUOUS MONITORING MODE")
    print("Press Ctrl+C to stop")
    print("-" * 30)
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            print(f"\n🔍 Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            async with StandaloneCryptoProvider() as provider:
                prices = await provider.get_all_prices(['BTC/USD', 'ETH/USD', 'BNB/USD'])
                opportunities = provider.detect_arbitrage_opportunities(prices, 0.001)
                
                if opportunities:
                    best = opportunities[0]
                    print(f"💰 Best: {best['symbol']} - {best['profit_percentage']:.3%} profit")
                    print(f"   {best['buy_exchange']} → {best['sell_exchange']}")
                    
                    if best['profit_percentage'] > 0.01:  # > 1%
                        print("🚨 HIGH PROFIT ALERT!")
                else:
                    print("❌ No opportunities")
            
            await asyncio.sleep(60)  # 1 minute intervals
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Monitoring stopped after {cycle} cycles")

async def main():
    """Main function."""
    await test_crypto_arbitrage()
    
    print("\n" + "=" * 50)
    choice = input("🤖 Start continuous monitoring? (y/n): ").lower().strip()
    
    if choice == 'y':
        await continuous_monitoring()
    
    print("\n✅ Test completed!")
    print("🎯 Ready for integration with Hephaestus financial system!")

if __name__ == "__main__":
    asyncio.run(main())