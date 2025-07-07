#!/usr/bin/env python3
"""
CRYPTO HUNTER 24/7 - Sistema de detecção de arbitragem em tempo real
Monitoramento contínuo com múltiplas exchanges e alertas inteligentes.
"""

import asyncio
import aiohttp
import logging
import json
import csv
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import colorama
from colorama import Fore, Back, Style
import time
import signal
import sys

# Initialize colorama for colored output
colorama.init()

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

@dataclass
class ArbitrageAlert:
    """Arbitrage opportunity alert."""
    symbol: str
    profit_percentage: float
    profit_amount: float
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    confidence: float
    timestamp: datetime
    potential_returns: Dict[str, float]
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'formatted_time': self.timestamp.strftime('%H:%M:%S')
        }

class CryptoHunter247:
    """24/7 Crypto arbitrage hunter with multiple exchanges."""
    
    def __init__(self):
        self.session = None
        self.logger = self._setup_logger()
        self.running = False
        self.stats = {
            'total_scans': 0,
            'opportunities_found': 0,
            'high_profit_alerts': 0,
            'exchanges_monitored': 0,
            'uptime_start': None,
            'last_opportunity': None
        }
        
        # Configuration
        self.PROFIT_THRESHOLD = 0.0001  # 0.01% - micro arbitrage
        self.HIGH_PROFIT_THRESHOLD = 0.005  # 0.5% - high profit alert
        self.SCAN_INTERVAL = 10  # 10 seconds
        self.ALERT_COOLDOWN = 30  # 30 seconds between same symbol alerts
        
        # Exchanges configuration
        self.exchanges = {
            'coingecko': {
                'name': 'CoinGecko',
                'base_url': 'https://api.coingecko.com/api/v3',
                'rate_limit': 10,
                'active': True
            },
            'binance': {
                'name': 'Binance',
                'base_url': 'https://api.binance.com/api/v3',
                'rate_limit': 1200,
                'active': True
            },
            'coinbase': {
                'name': 'Coinbase Pro',
                'base_url': 'https://api.exchange.coinbase.com',
                'rate_limit': 10,
                'active': True
            },
            'kraken': {
                'name': 'Kraken',
                'base_url': 'https://api.kraken.com/0/public',
                'rate_limit': 1,
                'active': True
            },
            'bitfinex': {
                'name': 'Bitfinex',
                'base_url': 'https://api-pub.bitfinex.com/v2',
                'rate_limit': 30,
                'active': True
            },
            'kucoin': {
                'name': 'KuCoin',
                'base_url': 'https://api.kucoin.com/api/v1',
                'rate_limit': 100,
                'active': True
            }
        }
        
        # Symbols to monitor
        self.symbols = [
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'ADA/USD', 'SOL/USD',
            'XRP/USD', 'DOT/USD', 'LINK/USD', 'AVAX/USD', 'MATIC/USD'
        ]
        
        # Alert tracking
        self.last_alerts = {}
        self.opportunity_log = []
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console output."""
        logger = logging.getLogger('CryptoHunter247')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('crypto_hunter_24_7.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n{Fore.YELLOW}🛑 Shutdown signal received. Stopping gracefully...{Style.RESET_ALL}")
        self.running = False
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_coingecko_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from CoinGecko API."""
        try:
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'ADA': 'cardano', 'SOL': 'solana', 'XRP': 'ripple',
                'DOT': 'polkadot', 'LINK': 'chainlink', 'AVAX': 'avalanche-2',
                'MATIC': 'matic-network'
            }
            
            ids = [symbol_map.get(s.replace('/USD', ''), s.lower()) for s in symbols if s.replace('/USD', '') in symbol_map]
            if not ids:
                return []
            
            ids_str = ','.join(ids)
            
            url = f"{self.exchanges['coingecko']['base_url']}/simple/price"
            params = {
                'ids': ids_str,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    prices = []
                    for coin_id, price_data in data.items():
                        if 'usd' in price_data:
                            prices.append(CryptoPrice(
                                symbol=coin_id.upper(),
                                exchange='coingecko',
                                price=price_data['usd'],
                                volume=price_data.get('usd_24h_vol', 0),
                                timestamp=datetime.fromtimestamp(price_data.get('last_updated_at', time.time()))
                            ))
                    
                    return prices
                
        except Exception as e:
            self.logger.debug(f"CoinGecko error: {e}")
            return []
    
    async def get_binance_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from Binance API."""
        try:
            url = f"{self.exchanges['binance']['base_url']}/ticker/24hr"
            
            async with self.session.get(url) as response:
                if response.status == 200:
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
            self.logger.debug(f"Binance error: {e}")
            return []
    
    async def get_coinbase_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from Coinbase Pro API."""
        try:
            prices = []
            
            for symbol in symbols:
                cb_symbol = symbol.replace('/', '-')
                url = f"{self.exchanges['coinbase']['base_url']}/products/{cb_symbol}/ticker"
                
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            prices.append(CryptoPrice(
                                symbol=symbol,
                                exchange='coinbase',
                                price=float(data['price']),
                                volume=float(data['volume']),
                                timestamp=datetime.fromisoformat(data['time'].replace('Z', '+00:00')).replace(tzinfo=None),
                                bid=float(data['bid']),
                                ask=float(data['ask'])
                            ))
                except:
                    continue
            
            return prices
            
        except Exception as e:
            self.logger.debug(f"Coinbase error: {e}")
            return []
    
    async def get_kraken_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from Kraken API."""
        try:
            # Kraken symbol mapping
            kraken_map = {
                'BTC/USD': 'XXBTZUSD',
                'ETH/USD': 'XETHZUSD',
                'ADA/USD': 'ADAUSD',
                'SOL/USD': 'SOLUSD',
                'XRP/USD': 'XXRPZUSD',
                'DOT/USD': 'DOTUSD',
                'LINK/USD': 'LINKUSD',
                'AVAX/USD': 'AVAXUSD',
                'MATIC/USD': 'MATICUSD'
            }
            
            kraken_symbols = [kraken_map.get(s) for s in symbols if s in kraken_map]
            if not kraken_symbols:
                return []
            
            url = f"{self.exchanges['kraken']['base_url']}/Ticker"
            params = {'pair': ','.join(kraken_symbols)}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('error'):
                        return []
                    
                    prices = []
                    result = data.get('result', {})
                    
                    for kraken_symbol, price_data in result.items():
                        # Find original symbol
                        original_symbol = None
                        for orig, kraken in kraken_map.items():
                            if kraken == kraken_symbol:
                                original_symbol = orig
                                break
                        
                        if original_symbol and 'c' in price_data:
                            prices.append(CryptoPrice(
                                symbol=original_symbol,
                                exchange='kraken',
                                price=float(price_data['c'][0]),  # Last trade price
                                volume=float(price_data['v'][1]),  # 24h volume
                                timestamp=datetime.now(),
                                bid=float(price_data['b'][0]) if 'b' in price_data else None,
                                ask=float(price_data['a'][0]) if 'a' in price_data else None
                            ))
                    
                    return prices
                
        except Exception as e:
            self.logger.debug(f"Kraken error: {e}")
            return []
    
    async def get_bitfinex_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from Bitfinex API."""
        try:
            # Bitfinex symbol mapping
            bitfinex_map = {
                'BTC/USD': 'tBTCUSD',
                'ETH/USD': 'tETHUSD',
                'ADA/USD': 'tADAUSD',
                'SOL/USD': 'tSOLUSD',
                'XRP/USD': 'tXRPUSD',
                'DOT/USD': 'tDOTUSD',
                'LINK/USD': 'tLINK:USD',
                'AVAX/USD': 'tAVAX:USD',
                'MATIC/USD': 'tMATIC:USD'
            }
            
            prices = []
            
            for symbol in symbols:
                if symbol in bitfinex_map:
                    bitfinex_symbol = bitfinex_map[symbol]
                    url = f"{self.exchanges['bitfinex']['base_url']}/ticker/{bitfinex_symbol}"
                    
                    try:
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                if len(data) >= 7:  # Ensure we have enough data
                                    prices.append(CryptoPrice(
                                        symbol=symbol,
                                        exchange='bitfinex',
                                        price=float(data[6]),  # Last price
                                        volume=float(data[7]),  # Volume
                                        timestamp=datetime.now(),
                                        bid=float(data[0]),    # Bid
                                        ask=float(data[2])     # Ask
                                    ))
                    except:
                        continue
            
            return prices
            
        except Exception as e:
            self.logger.debug(f"Bitfinex error: {e}")
            return []
    
    async def get_kucoin_prices(self, symbols: List[str]) -> List[CryptoPrice]:
        """Get prices from KuCoin API."""
        try:
            url = f"{self.exchanges['kucoin']['base_url']}/market/allTickers"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('code') != '200000':
                        return []
                    
                    tickers = data.get('data', {}).get('ticker', [])
                    
                    prices = []
                    kucoin_map = {
                        'BTC-USDT': 'BTC/USD',
                        'ETH-USDT': 'ETH/USD',
                        'BNB-USDT': 'BNB/USD',
                        'ADA-USDT': 'ADA/USD',
                        'SOL-USDT': 'SOL/USD',
                        'XRP-USDT': 'XRP/USD',
                        'DOT-USDT': 'DOT/USD',
                        'LINK-USDT': 'LINK/USD',
                        'AVAX-USDT': 'AVAX/USD',
                        'MATIC-USDT': 'MATIC/USD'
                    }
                    
                    for ticker in tickers:
                        kucoin_symbol = ticker.get('symbol')
                        if kucoin_symbol in kucoin_map:
                            symbol = kucoin_map[kucoin_symbol]
                            prices.append(CryptoPrice(
                                symbol=symbol,
                                exchange='kucoin',
                                price=float(ticker['last']),
                                volume=float(ticker['vol']),
                                timestamp=datetime.now(),
                                bid=float(ticker['buy']) if ticker['buy'] else None,
                                ask=float(ticker['sell']) if ticker['sell'] else None
                            ))
                    
                    return prices
                
        except Exception as e:
            self.logger.debug(f"KuCoin error: {e}")
            return []
    
    async def get_all_prices(self) -> Dict[str, List[CryptoPrice]]:
        """Get prices from all active exchanges."""
        tasks = []
        
        if self.exchanges['coingecko']['active']:
            tasks.append(self.get_coingecko_prices(self.symbols))
        if self.exchanges['binance']['active']:
            tasks.append(self.get_binance_prices(self.symbols))
        if self.exchanges['coinbase']['active']:
            tasks.append(self.get_coinbase_prices(self.symbols))
        if self.exchanges['kraken']['active']:
            tasks.append(self.get_kraken_prices(self.symbols))
        if self.exchanges['bitfinex']['active']:
            tasks.append(self.get_bitfinex_prices(self.symbols))
        if self.exchanges['kucoin']['active']:
            tasks.append(self.get_kucoin_prices(self.symbols))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_prices = {}
        active_exchanges = 0
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            if result is None:
                continue
                
            active_exchanges += 1
            for price in result:
                if price.symbol not in all_prices:
                    all_prices[price.symbol] = []
                all_prices[price.symbol].append(price)
        
        self.stats['exchanges_monitored'] = active_exchanges
        return all_prices
    
    def detect_arbitrage_opportunities(self, prices: Dict[str, List[CryptoPrice]]) -> List[ArbitrageAlert]:
        """Detect arbitrage opportunities with enhanced analysis."""
        opportunities = []
        
        for symbol, price_list in prices.items():
            if len(price_list) < 2:
                continue
            
            # Sort by price
            sorted_prices = sorted(price_list, key=lambda x: x.price)
            lowest = sorted_prices[0]
            highest = sorted_prices[-1]
            
            # Calculate profit (avoid division by zero)
            if lowest.price <= 0:
                continue
            profit_percentage = (highest.price - lowest.price) / lowest.price
            
            if profit_percentage >= self.PROFIT_THRESHOLD:
                # Calculate potential returns for different investment amounts
                investment_amounts = [100, 1000, 10000, 50000]
                potential_returns = {}
                
                for amount in investment_amounts:
                    units = amount / lowest.price
                    profit = units * (highest.price - lowest.price)
                    potential_returns[f"${amount}"] = round(profit, 2)
                
                alert = ArbitrageAlert(
                    symbol=symbol,
                    profit_percentage=profit_percentage,
                    profit_amount=highest.price - lowest.price,
                    buy_exchange=lowest.exchange,
                    sell_exchange=highest.exchange,
                    buy_price=lowest.price,
                    sell_price=highest.price,
                    confidence=self._calculate_confidence(lowest, highest),
                    timestamp=datetime.now(),
                    potential_returns=potential_returns
                )
                
                opportunities.append(alert)
        
        return sorted(opportunities, key=lambda x: x.profit_percentage, reverse=True)
    
    def _calculate_confidence(self, buy_price: CryptoPrice, sell_price: CryptoPrice) -> float:
        """Calculate confidence score for arbitrage opportunity."""
        confidence = 0.5
        
        # Volume factor
        if buy_price.volume > 1000000:
            confidence += 0.2
        if sell_price.volume > 1000000:
            confidence += 0.2
        
        # Timestamp factor
        now = datetime.now()
        if (now - buy_price.timestamp).seconds < 300:
            confidence += 0.1
        if (now - sell_price.timestamp).seconds < 300:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def should_alert(self, alert: ArbitrageAlert) -> bool:
        """Check if we should send alert based on cooldown."""
        key = f"{alert.symbol}_{alert.buy_exchange}_{alert.sell_exchange}"
        now = datetime.now()
        
        if key in self.last_alerts:
            time_diff = (now - self.last_alerts[key]).seconds
            if time_diff < self.ALERT_COOLDOWN:
                return False
        
        self.last_alerts[key] = now
        return True
    
    def print_alert(self, alert: ArbitrageAlert):
        """Print formatted alert to console."""
        is_high_profit = alert.profit_percentage >= self.HIGH_PROFIT_THRESHOLD
        
        if is_high_profit:
            print(f"\n{Back.RED}{Fore.WHITE}🚨 HIGH PROFIT ALERT! 🚨{Style.RESET_ALL}")
            self.stats['high_profit_alerts'] += 1
        else:
            print(f"\n{Fore.GREEN}💰 ARBITRAGE OPPORTUNITY{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Symbol:{Style.RESET_ALL} {alert.symbol}")
        print(f"{Fore.YELLOW}Profit:{Style.RESET_ALL} {alert.profit_percentage:.4%} (${alert.profit_amount:.2f} per unit)")
        print(f"{Fore.BLUE}Buy:{Style.RESET_ALL} {alert.buy_exchange} @ ${alert.buy_price:,.2f}")
        print(f"{Fore.MAGENTA}Sell:{Style.RESET_ALL} {alert.sell_exchange} @ ${alert.sell_price:,.2f}")
        print(f"{Fore.WHITE}Confidence:{Style.RESET_ALL} {alert.confidence:.2f}")
        print(f"{Fore.GREEN}Potential Returns:{Style.RESET_ALL}")
        
        for investment, profit in alert.potential_returns.items():
            roi = (profit / float(investment.replace('$', ''))) * 100
            print(f"  {investment} → ${profit:.2f} profit ({roi:.2f}% ROI)")
        
        print("-" * 50)
    
    def save_opportunity(self, alert: ArbitrageAlert):
        """Save opportunity to CSV log."""
        log_file = 'crypto_opportunities_24_7.csv'
        file_exists = os.path.exists(log_file)
        
        with open(log_file, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'symbol', 'profit_percentage', 'profit_amount', 
                         'buy_exchange', 'sell_exchange', 'buy_price', 'sell_price', 
                         'confidence', 'potential_100', 'potential_1000', 'potential_10000']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': alert.timestamp.isoformat(),
                'symbol': alert.symbol,
                'profit_percentage': alert.profit_percentage,
                'profit_amount': alert.profit_amount,
                'buy_exchange': alert.buy_exchange,
                'sell_exchange': alert.sell_exchange,
                'buy_price': alert.buy_price,
                'sell_price': alert.sell_price,
                'confidence': alert.confidence,
                'potential_100': alert.potential_returns.get('$100', 0),
                'potential_1000': alert.potential_returns.get('$1000', 0),
                'potential_10000': alert.potential_returns.get('$10000', 0)
            })
    
    def print_status(self, opportunities: List[ArbitrageAlert]):
        """Print current status."""
        now = datetime.now()
        uptime = now - self.stats['uptime_start'] if self.stats['uptime_start'] else timedelta(0)
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}🤖 CRYPTO HUNTER 24/7 - LIVE MONITORING{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}⏰ Time:{Style.RESET_ALL} {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.BLUE}⏱️  Uptime:{Style.RESET_ALL} {uptime}")
        print(f"{Fore.YELLOW}🔍 Scans:{Style.RESET_ALL} {self.stats['total_scans']}")
        print(f"{Fore.MAGENTA}🎯 Opportunities:{Style.RESET_ALL} {self.stats['opportunities_found']}")
        print(f"{Fore.RED}🚨 High Profit Alerts:{Style.RESET_ALL} {self.stats['high_profit_alerts']}")
        print(f"{Fore.CYAN}📊 Exchanges:{Style.RESET_ALL} {self.stats['exchanges_monitored']}")
        
        if opportunities:
            print(f"\n{Fore.GREEN}💰 CURRENT OPPORTUNITIES ({len(opportunities)}):{Style.RESET_ALL}")
            for i, opp in enumerate(opportunities[:5], 1):
                profit_color = Fore.RED if opp.profit_percentage >= self.HIGH_PROFIT_THRESHOLD else Fore.GREEN
                print(f"  {i}. {opp.symbol}: {profit_color}{opp.profit_percentage:.4%}{Style.RESET_ALL}")
                print(f"     {opp.buy_exchange} → {opp.sell_exchange} (${opp.profit_amount:.2f}/unit)")
        else:
            print(f"\n{Fore.YELLOW}❌ No opportunities found this cycle{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    async def hunt_24_7(self):
        """Main 24/7 hunting loop."""
        self.running = True
        self.stats['uptime_start'] = datetime.now()
        
        print(f"{Fore.GREEN}🚀 STARTING CRYPTO HUNTER 24/7{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Configuration:{Style.RESET_ALL}")
        print(f"  Profit Threshold: {self.PROFIT_THRESHOLD:.4%}")
        print(f"  High Profit Alert: {self.HIGH_PROFIT_THRESHOLD:.2%}")
        print(f"  Scan Interval: {self.SCAN_INTERVAL} seconds")
        print(f"  Symbols: {len(self.symbols)}")
        print(f"  Exchanges: {sum(1 for ex in self.exchanges.values() if ex['active'])}")
        print(f"\n{Fore.YELLOW}Press Ctrl+C to stop gracefully{Style.RESET_ALL}\n")
        
        try:
            while self.running:
                cycle_start = time.time()
                
                # Get prices from all exchanges
                prices = await self.get_all_prices()
                
                # Detect opportunities
                opportunities = self.detect_arbitrage_opportunities(prices)
                
                # Update stats
                self.stats['total_scans'] += 1
                if opportunities:
                    self.stats['opportunities_found'] += len(opportunities)
                    self.stats['last_opportunity'] = datetime.now()
                
                # Process alerts
                for opportunity in opportunities:
                    if self.should_alert(opportunity):
                        self.print_alert(opportunity)
                        self.save_opportunity(opportunity)
                
                # Print status every 10 scans or if opportunities found
                if self.stats['total_scans'] % 10 == 0 or opportunities:
                    self.print_status(opportunities)
                
                # Calculate sleep time to maintain interval
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, self.SCAN_INTERVAL - cycle_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    self.logger.warning(f"Cycle took {cycle_time:.2f}s, longer than {self.SCAN_INTERVAL}s interval")
                
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Cleanup and print final stats."""
        print(f"\n{Fore.YELLOW}🛑 CRYPTO HUNTER 24/7 STOPPED{Style.RESET_ALL}")
        
        uptime = datetime.now() - self.stats['uptime_start'] if self.stats['uptime_start'] else timedelta(0)
        
        print(f"\n{Fore.CYAN}📊 FINAL STATISTICS:{Style.RESET_ALL}")
        print(f"Total Uptime: {uptime}")
        print(f"Total Scans: {self.stats['total_scans']}")
        print(f"Opportunities Found: {self.stats['opportunities_found']}")
        print(f"High Profit Alerts: {self.stats['high_profit_alerts']}")
        
        if self.stats['total_scans'] > 0:
            opp_rate = (self.stats['opportunities_found'] / self.stats['total_scans']) * 100
            print(f"Opportunity Rate: {opp_rate:.2f}%")
        
        print(f"\n{Fore.GREEN}📄 Opportunities logged to: crypto_opportunities_24_7.csv{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📄 Full logs saved to: crypto_hunter_24_7.log{Style.RESET_ALL}")

async def main():
    """Main function."""
    print(f"{Fore.GREEN}🚀 CRYPTO HUNTER 24/7 - ULTIMATE ARBITRAGE DETECTOR{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    async with CryptoHunter247() as hunter:
        await hunter.hunt_24_7()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)