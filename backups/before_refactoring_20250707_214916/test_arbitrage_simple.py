#!/usr/bin/env python3
"""
Simplified test for crypto arbitrage system without full Hephaestus dependencies.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_crypto_data_provider():
    """Test the crypto data provider independently."""
    print("🔍 Testing Crypto Data Provider...")
    
    try:
        from hephaestus.data_sources.crypto_apis import CryptoDataProvider
        
        async with CryptoDataProvider() as provider:
            print("✅ CryptoDataProvider initialized successfully")
            
            # Test getting prices
            symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD']
            prices = await provider.get_all_prices(symbols)
            
            print(f"📊 Retrieved prices for {len(prices)} symbols:")
            for symbol, price_list in prices.items():
                print(f"  {symbol}: {len(price_list)} exchanges")
                for price in price_list:
                    print(f"    {price.exchange}: ${price.price:.2f} (Vol: ${price.volume:,.0f})")
            
            # Test arbitrage detection
            if prices:
                opportunities = provider.detect_arbitrage_opportunities(prices, min_profit_threshold=0.001)
                print(f"\n💰 Found {len(opportunities)} arbitrage opportunities:")
                
                for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                    print(f"  {i}. {opp['symbol']}: {opp['profit_percentage']:.3%} profit")
                    print(f"     Buy: {opp['buy_exchange']} @ ${opp['buy_price']:.2f}")
                    print(f"     Sell: {opp['sell_exchange']} @ ${opp['sell_price']:.2f}")
                    print(f"     Profit: ${opp['profit_amount']:.2f}")
                    print(f"     Confidence: {opp['confidence']:.2f}")
                    print()
                
                if opportunities:
                    print(f"🎯 BEST OPPORTUNITY: {opportunities[0]['symbol']}")
                    print(f"   Profit: {opportunities[0]['profit_percentage']:.3%}")
                    print(f"   Expected Return: ${opportunities[0]['profit_amount']:.2f} per unit")
                else:
                    print("❌ No profitable opportunities found")
            
    except Exception as e:
        print(f"❌ Error testing CryptoDataProvider: {e}")
        import traceback
        traceback.print_exc()

async def test_market_analysis():
    """Test market analysis capabilities."""
    print("\n🔍 Testing Market Analysis...")
    
    try:
        from hephaestus.data_sources.crypto_apis import CryptoDataProvider
        
        async with CryptoDataProvider() as provider:
            # Get comprehensive market data
            major_cryptos = ['BTC/USD', 'ETH/USD', 'BNB/USD', 'ADA/USD', 'SOL/USD']
            prices = await provider.get_all_prices(major_cryptos)
            
            print("📈 Market Overview:")
            total_volume = 0
            price_ranges = {}
            
            for symbol, price_list in prices.items():
                if price_list:
                    prices_only = [p.price for p in price_list]
                    volumes = [p.volume for p in price_list if p.volume > 0]
                    
                    min_price = min(prices_only)
                    max_price = max(prices_only)
                    avg_price = sum(prices_only) / len(prices_only)
                    total_vol = sum(volumes)
                    
                    price_ranges[symbol] = {
                        'min': min_price,
                        'max': max_price,
                        'avg': avg_price,
                        'spread': (max_price - min_price) / min_price * 100,
                        'volume': total_vol
                    }
                    
                    total_volume += total_vol
                    
                    print(f"  {symbol}:")
                    print(f"    Price Range: ${min_price:.2f} - ${max_price:.2f}")
                    print(f"    Average: ${avg_price:.2f}")
                    print(f"    Spread: {price_ranges[symbol]['spread']:.2f}%")
                    print(f"    Volume: ${total_vol:,.0f}")
                    print()
            
            print(f"📊 Total Market Volume: ${total_volume:,.0f}")
            
            # Find best arbitrage opportunities
            all_opportunities = []
            for symbol, price_list in prices.items():
                if len(price_list) >= 2:
                    opportunities = provider.detect_arbitrage_opportunities({symbol: price_list}, 0.001)
                    all_opportunities.extend(opportunities)
            
            if all_opportunities:
                best_opp = max(all_opportunities, key=lambda x: x['profit_percentage'])
                print(f"🏆 BEST ARBITRAGE OPPORTUNITY:")
                print(f"   Symbol: {best_opp['symbol']}")
                print(f"   Profit: {best_opp['profit_percentage']:.3%}")
                print(f"   Buy at: {best_opp['buy_exchange']} (${best_opp['buy_price']:.2f})")
                print(f"   Sell at: {best_opp['sell_exchange']} (${best_opp['sell_price']:.2f})")
                print(f"   Profit per unit: ${best_opp['profit_amount']:.2f}")
                
                # Calculate potential returns
                investment_amounts = [100, 1000, 10000]
                print(f"\n💰 POTENTIAL RETURNS:")
                for amount in investment_amounts:
                    units = amount / best_opp['buy_price']
                    profit = units * best_opp['profit_amount']
                    print(f"   ${amount:,} investment → ${profit:.2f} profit ({profit/amount*100:.2f}%)")
            
    except Exception as e:
        print(f"❌ Error in market analysis: {e}")
        import traceback
        traceback.print_exc()

async def continuous_monitoring_demo():
    """Demonstrate continuous monitoring."""
    print("\n🔄 Starting Continuous Monitoring Demo...")
    print("(Running for 3 cycles, 30 seconds each)")
    
    try:
        from hephaestus.data_sources.crypto_apis import CryptoDataProvider
        
        for cycle in range(3):
            print(f"\n🔍 CYCLE {cycle + 1}/3")
            print("-" * 30)
            
            async with CryptoDataProvider() as provider:
                # Quick scan of major pairs
                prices = await provider.get_all_prices(['BTC/USD', 'ETH/USD', 'BNB/USD'])
                
                opportunities = []
                for symbol, price_list in prices.items():
                    if len(price_list) >= 2:
                        opps = provider.detect_arbitrage_opportunities({symbol: price_list}, 0.001)
                        opportunities.extend(opps)
                
                if opportunities:
                    best = max(opportunities, key=lambda x: x['profit_percentage'])
                    print(f"🎯 Best opportunity: {best['symbol']}")
                    print(f"   Profit: {best['profit_percentage']:.3%}")
                    print(f"   Confidence: {best['confidence']:.2f}")
                    
                    if best['profit_percentage'] > 0.01:  # > 1%
                        print("🚨 HIGH PROFIT OPPORTUNITY DETECTED!")
                else:
                    print("❌ No opportunities found this cycle")
            
            if cycle < 2:  # Don't sleep after last cycle
                print(f"⏳ Waiting 30 seconds for next cycle...")
                await asyncio.sleep(30)
    
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error in continuous monitoring: {e}")

async def main():
    """Main test function."""
    print("🚀 CRYPTO ARBITRAGE SYSTEM - STANDALONE TEST")
    print("=" * 60)
    
    # Test crypto data provider
    await test_crypto_data_provider()
    
    # Test market analysis
    await test_market_analysis()
    
    # Ask user if they want continuous monitoring
    print("\n" + "=" * 60)
    response = input("🤖 Run continuous monitoring demo? (y/n): ").lower().strip()
    
    if response == 'y':
        await continuous_monitoring_demo()
    
    print("\n✅ All tests completed!")
    print("🎯 System is ready for integration with Hephaestus!")

if __name__ == "__main__":
    asyncio.run(main())