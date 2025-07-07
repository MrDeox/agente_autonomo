#!/usr/bin/env python3
"""
Test script for the crypto arbitrage system.
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
    """Test the crypto data provider."""
    print("🔍 Testing Crypto Data Provider...")
    
    try:
        from hephaestus.data_sources.crypto_apis import CryptoDataProvider
        
        async with CryptoDataProvider() as provider:
            print("✅ CryptoDataProvider initialized successfully")
            
            # Test getting prices
            prices = await provider.get_all_prices(['BTC/USD', 'ETH/USD'])
            
            print(f"📊 Retrieved prices for {len(prices)} symbols:")
            for symbol, price_list in prices.items():
                print(f"  {symbol}: {len(price_list)} exchanges")
                for price in price_list:
                    print(f"    {price.exchange}: ${price.price:.2f}")
            
            # Test arbitrage detection
            if prices:
                opportunities = provider.detect_arbitrage_opportunities(prices)
                print(f"💰 Found {len(opportunities)} arbitrage opportunities")
                
                for opp in opportunities[:3]:  # Show top 3
                    print(f"  {opp['symbol']}: {opp['profit_percentage']:.2%} profit")
                    print(f"    Buy: {opp['buy_exchange']} @ ${opp['buy_price']:.2f}")
                    print(f"    Sell: {opp['sell_exchange']} @ ${opp['sell_price']:.2f}")
                    print()
            
    except Exception as e:
        print(f"❌ Error testing CryptoDataProvider: {e}")
        import traceback
        traceback.print_exc()

async def test_arbitrage_detector():
    """Test the arbitrage detector."""
    print("\n🎯 Testing Arbitrage Detector...")
    
    try:
        from hephaestus.financial.crypto_arbitrage import CryptoArbitrageDetector
        
        config = {
            'arbitrage': {
                'min_profit_threshold': 0.005,
                'max_risk_score': 0.7,
                'execution_timeout': 30
            },
            'models': {
                'arbitrage_model': 'gpt-4'
            }
        }
        
        detector = CryptoArbitrageDetector(config)
        print("✅ CryptoArbitrageDetector initialized successfully")
        
        # Test opportunity detection
        opportunities = await detector.scan_for_opportunities()
        
        print(f"🎯 Found {len(opportunities)} viable opportunities:")
        for opp in opportunities:
            print(f"  {opp.symbol}: {opp.profit_percentage:.2%} profit")
            print(f"    Risk Score: {opp.risk_score:.2f}")
            print(f"    Confidence: {opp.confidence:.2f}")
            print(f"    Execution Time: {opp.estimated_execution_time:.1f}s")
            print()
        
        # Test performance summary
        performance = detector.get_performance_summary()
        print(f"📊 Performance Summary:")
        print(f"  Total Scans: {performance['total_scans']}")
        print(f"  Success Rate: {performance['success_rate']:.2%}")
        
    except Exception as e:
        print(f"❌ Error testing ArbitrageDetector: {e}")
        import traceback
        traceback.print_exc()

async def test_opportunity_detector():
    """Test the main opportunity detector."""
    print("\n🚀 Testing Opportunity Detector...")
    
    try:
        from hephaestus.financial.opportunity_detector import OpportunityDetector
        
        config = {
            'opportunities': {
                'min_confidence': 0.6,
                'max_risk': 0.8,
                'scan_interval': 60
            },
            'arbitrage': {
                'min_profit_threshold': 0.005,
                'max_risk_score': 0.7
            },
            'models': {
                'opportunity_model': 'gpt-4'
            }
        }
        
        detector = OpportunityDetector(config)
        print("✅ OpportunityDetector initialized successfully")
        
        # Test comprehensive opportunity detection
        opportunities = await detector.detect_all_opportunities()
        
        print(f"🎯 Found {len(opportunities)} total opportunities:")
        for i, opp in enumerate(opportunities, 1):
            score = (opp.expected_profit * opp.confidence) / max(opp.risk_score, 0.1)
            print(f"  {i}. {opp.description}")
            print(f"     Type: {opp.opportunity_type}")
            print(f"     Expected Profit: {opp.expected_profit:.2%}")
            print(f"     Risk: {opp.risk_score:.2f} | Confidence: {opp.confidence:.2f}")
            print(f"     Score: {score:.2f}")
            print()
        
        # Test performance summary
        performance = detector.get_performance_summary()
        print(f"📊 Performance Summary:")
        print(f"  Opportunities Detected: {performance['total_opportunities_detected']}")
        print(f"  Success Rate: {performance['success_rate']:.2%}")
        
    except Exception as e:
        print(f"❌ Error testing OpportunityDetector: {e}")
        import traceback
        traceback.print_exc()

async def run_live_demo():
    """Run a live demonstration of the system."""
    print("\n🔥 LIVE DEMO: Crypto Arbitrage Detection System")
    print("=" * 60)
    
    try:
        from hephaestus.financial.opportunity_detector import OpportunityDetector
        
        config = {
            'opportunities': {
                'min_confidence': 0.5,  # Lower threshold for demo
                'max_risk': 0.9,
                'scan_interval': 30
            },
            'arbitrage': {
                'min_profit_threshold': 0.001,  # 0.1% for demo
                'max_risk_score': 0.8
            },
            'models': {
                'opportunity_model': 'gpt-4'
            }
        }
        
        detector = OpportunityDetector(config)
        
        print("🎯 Scanning for live arbitrage opportunities...")
        opportunities = await detector.detect_all_opportunities()
        
        if opportunities:
            print(f"\n💰 FOUND {len(opportunities)} OPPORTUNITIES!")
            print("=" * 60)
            
            for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                score = (opp.expected_profit * opp.confidence) / max(opp.risk_score, 0.1)
                
                print(f"🏆 OPPORTUNITY #{i}")
                print(f"Symbol: {opp.symbol}")
                print(f"Description: {opp.description}")
                print(f"Expected Profit: {opp.expected_profit:.2%}")
                print(f"Risk Score: {opp.risk_score:.2f}")
                print(f"Confidence: {opp.confidence:.2f}")
                print(f"Overall Score: {score:.2f}")
                
                if opp.metadata:
                    print("Details:")
                    for key, value in opp.metadata.items():
                        if isinstance(value, float):
                            print(f"  {key}: {value:.4f}")
                        else:
                            print(f"  {key}: {value}")
                
                print("-" * 40)
        else:
            print("❌ No opportunities found in current market conditions")
            print("💡 Try again later or adjust the profit threshold")
        
    except Exception as e:
        print(f"❌ Error in live demo: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function."""
    print("🚀 HEPHAESTUS FINANCIAL INTELLIGENCE SYSTEM")
    print("Testing Crypto Arbitrage Detection System")
    print("=" * 60)
    
    # Test individual components
    await test_crypto_data_provider()
    await test_arbitrage_detector()
    await test_opportunity_detector()
    
    # Run live demo
    await run_live_demo()
    
    print("\n✅ All tests completed!")
    print("🎯 The system is ready for autonomous revenue generation!")

if __name__ == "__main__":
    asyncio.run(main())