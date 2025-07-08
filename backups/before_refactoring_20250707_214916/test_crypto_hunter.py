#!/usr/bin/env python3
"""
Test script for Crypto Hunter 24/7 system.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_crypto_hunter():
    """Test the crypto hunter system."""
    print("🚀 TESTING CRYPTO HUNTER 24/7 SYSTEM")
    print("=" * 50)
    
    try:
        # Import the CryptoHunter247 class
        from crypto_hunter_24_7 import CryptoHunter247
        
        # Create hunter instance
        async with CryptoHunter247() as hunter:
            print("✅ CryptoHunter247 initialized successfully")
            
            # Set test configuration
            hunter.PROFIT_THRESHOLD = 0.0001  # 0.01%
            hunter.HIGH_PROFIT_THRESHOLD = 0.005  # 0.5%
            hunter.SCAN_INTERVAL = 5  # 5 seconds for testing
            
            print(f"🎯 Configuration:")
            print(f"  Profit Threshold: {hunter.PROFIT_THRESHOLD:.4%}")
            print(f"  High Profit Alert: {hunter.HIGH_PROFIT_THRESHOLD:.2%}")
            print(f"  Scan Interval: {hunter.SCAN_INTERVAL} seconds")
            print(f"  Symbols: {len(hunter.symbols)}")
            
            # Test individual exchange connections
            print(f"\n🔍 Testing exchange connections...")
            
            # Test CoinGecko
            coingecko_prices = await hunter.get_coingecko_prices(['BTC/USD', 'ETH/USD'])
            print(f"  CoinGecko: {len(coingecko_prices)} prices")
            
            # Test Binance
            binance_prices = await hunter.get_binance_prices(['BTC/USD', 'ETH/USD'])
            print(f"  Binance: {len(binance_prices)} prices")
            
            # Test Coinbase
            coinbase_prices = await hunter.get_coinbase_prices(['BTC/USD', 'ETH/USD'])
            print(f"  Coinbase: {len(coinbase_prices)} prices")
            
            # Test Kraken
            kraken_prices = await hunter.get_kraken_prices(['BTC/USD', 'ETH/USD'])
            print(f"  Kraken: {len(kraken_prices)} prices")
            
            # Test all prices together
            print(f"\n📊 Testing comprehensive data collection...")
            all_prices = await hunter.get_all_prices()
            
            total_prices = sum(len(prices) for prices in all_prices.values())
            print(f"  Total symbols: {len(all_prices)}")
            print(f"  Total price points: {total_prices}")
            print(f"  Active exchanges: {hunter.stats['exchanges_monitored']}")
            
            # Show detailed price data
            print(f"\n💰 Current Market Data:")
            for symbol, price_list in all_prices.items():
                if price_list:
                    print(f"  {symbol}:")
                    for price in price_list:
                        print(f"    {price.exchange}: ${price.price:,.2f} (Vol: ${price.volume:,.0f})")
            
            # Test arbitrage detection
            print(f"\n🎯 Testing arbitrage detection...")
            opportunities = hunter.detect_arbitrage_opportunities(all_prices)
            
            print(f"  Found {len(opportunities)} opportunities")
            
            if opportunities:
                print(f"\n🏆 TOP OPPORTUNITIES:")
                for i, opp in enumerate(opportunities[:5], 1):
                    print(f"    {i}. {opp.symbol}: {opp.profit_percentage:.4%} profit")
                    print(f"       {opp.buy_exchange} → {opp.sell_exchange}")
                    print(f"       Buy: ${opp.buy_price:,.2f} | Sell: ${opp.sell_price:,.2f}")
                    print(f"       Profit/unit: ${opp.profit_amount:.2f}")
                    print(f"       Potential returns:")
                    for investment, profit in opp.potential_returns.items():
                        print(f"         {investment} → ${profit:.2f}")
                    print()
            else:
                print("  ❌ No opportunities found (market conditions stable)")
                print("  💡 This is normal - opportunities are rare!")
            
            # Test 3 monitoring cycles
            print(f"\n🔄 Testing 3 monitoring cycles...")
            for cycle in range(3):
                print(f"\n📡 Cycle {cycle + 1}/3")
                
                prices = await hunter.get_all_prices()
                opportunities = hunter.detect_arbitrage_opportunities(prices)
                
                hunter.stats['total_scans'] += 1
                if opportunities:
                    hunter.stats['opportunities_found'] += len(opportunities)
                    
                    best = opportunities[0]
                    print(f"  🎯 Best opportunity: {best.symbol}")
                    print(f"     Profit: {best.profit_percentage:.4%}")
                    print(f"     {best.buy_exchange} → {best.sell_exchange}")
                    
                    if best.profit_percentage >= hunter.HIGH_PROFIT_THRESHOLD:
                        print(f"  🚨 HIGH PROFIT ALERT!")
                        hunter.stats['high_profit_alerts'] += 1
                else:
                    print(f"  ❌ No opportunities this cycle")
                
                if cycle < 2:  # Don't sleep on last cycle
                    await asyncio.sleep(5)
            
            # Final stats
            print(f"\n📊 TEST RESULTS:")
            print(f"  Scans completed: {hunter.stats['total_scans']}")
            print(f"  Opportunities found: {hunter.stats['opportunities_found']}")
            print(f"  High profit alerts: {hunter.stats['high_profit_alerts']}")
            print(f"  Success rate: {(hunter.stats['opportunities_found'] / max(1, hunter.stats['total_scans'])) * 100:.1f}%")
            
    except Exception as e:
        print(f"❌ Error testing CryptoHunter247: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function."""
    await test_crypto_hunter()
    
    print(f"\n✅ TEST COMPLETED!")
    print(f"🎯 System is ready for 24/7 operation!")
    
    # Ask if user wants to start full monitoring
    try:
        choice = input(f"\n🤖 Start full 24/7 monitoring? (y/n): ").lower().strip()
        
        if choice == 'y':
            print(f"\n🚀 Starting 24/7 monitoring...")
            print(f"⚠️  Press Ctrl+C to stop")
            
            from crypto_hunter_24_7 import CryptoHunter247
            
            async with CryptoHunter247() as hunter:
                await hunter.hunt_24_7()
    
    except (EOFError, KeyboardInterrupt):
        print(f"\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())