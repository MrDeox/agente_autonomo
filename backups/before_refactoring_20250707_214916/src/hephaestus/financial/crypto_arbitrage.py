"""
Cryptocurrency arbitrage detection and execution engine.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from hephaestus.data_sources.crypto_apis import CryptoDataProvider, CryptoPrice
from hephaestus.intelligence.knowledge_system import get_knowledge_system
from hephaestus.intelligence.model_optimizer import get_model_optimizer
from hephaestus.intelligence.root_cause_analyzer import get_root_cause_analyzer

@dataclass
class ArbitrageOpportunity:
    """Structured arbitrage opportunity data."""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_percentage: float
    profit_amount: float
    confidence: float
    timestamp: datetime
    estimated_execution_time: float
    risk_score: float
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'buy_exchange': self.buy_exchange,
            'sell_exchange': self.sell_exchange,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'profit_percentage': self.profit_percentage,
            'profit_amount': self.profit_amount,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'estimated_execution_time': self.estimated_execution_time,
            'risk_score': self.risk_score
        }

class CryptoArbitrageDetector:
    """Advanced cryptocurrency arbitrage detection with AI-powered optimization."""
    
    def __init__(self, config: Dict, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.data_provider = CryptoDataProvider(logger)
        
        # Initialize AI components
        self.knowledge_system = get_knowledge_system(config, logger)
        self.model_optimizer = get_model_optimizer(
            config.get('models', {}).get('arbitrage_model', 'gpt-4'),
            logger
        )
        self.root_cause_analyzer = get_root_cause_analyzer(logger)
        
        # Arbitrage settings
        self.min_profit_threshold = config.get('arbitrage', {}).get('min_profit_threshold', 0.005)  # 0.5%
        self.max_risk_score = config.get('arbitrage', {}).get('max_risk_score', 0.7)
        self.execution_timeout = config.get('arbitrage', {}).get('execution_timeout', 30)  # seconds
        
        # Performance tracking
        self.successful_opportunities = []
        self.failed_opportunities = []
        self.total_scans = 0
        
    async def scan_for_opportunities(self) -> List[ArbitrageOpportunity]:
        """Scan all exchanges for arbitrage opportunities."""
        self.total_scans += 1
        self.logger.info(f"🔍 Starting arbitrage scan #{self.total_scans}")
        
        try:
            async with self.data_provider as provider:
                # Get prices from all exchanges
                prices = await provider.get_all_prices()
                
                # Detect basic arbitrage opportunities
                raw_opportunities = provider.detect_arbitrage_opportunities(
                    prices, self.min_profit_threshold
                )
                
                # Enhance with AI analysis
                enhanced_opportunities = []
                for opp in raw_opportunities:
                    enhanced_opp = await self._enhance_opportunity(opp, prices)
                    if enhanced_opp and enhanced_opp.risk_score <= self.max_risk_score:
                        enhanced_opportunities.append(enhanced_opp)
                
                self.logger.info(f"📊 Found {len(enhanced_opportunities)} viable opportunities")
                return enhanced_opportunities
                
        except Exception as e:
            self.logger.error(f"Error in arbitrage scan: {e}")
            await self._record_failure("scan_error", str(e))
            return []
    
    async def _enhance_opportunity(self, raw_opp: Dict, all_prices: Dict) -> Optional[ArbitrageOpportunity]:
        """Enhance opportunity with AI-powered analysis."""
        try:
            # Get market intelligence
            market_context = await self._get_market_context(raw_opp['symbol'])
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(raw_opp, market_context)
            
            # Estimate execution time
            execution_time = self._estimate_execution_time(raw_opp)
            
            opportunity = ArbitrageOpportunity(
                symbol=raw_opp['symbol'],
                buy_exchange=raw_opp['buy_exchange'],
                sell_exchange=raw_opp['sell_exchange'],
                buy_price=raw_opp['buy_price'],
                sell_price=raw_opp['sell_price'],
                profit_percentage=raw_opp['profit_percentage'],
                profit_amount=raw_opp['profit_amount'],
                confidence=raw_opp['confidence'],
                timestamp=raw_opp['timestamp'],
                estimated_execution_time=execution_time,
                risk_score=risk_score
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error enhancing opportunity: {e}")
            return None
    
    async def _get_market_context(self, symbol: str) -> Dict:
        """Get market context using knowledge system."""
        try:
            # Search for recent market news and trends
            search_query = f"{symbol} cryptocurrency price movement news today"
            
            search_results = await self.knowledge_system.intelligent_search(
                search_query,
                search_type="market_analysis",
                max_results=5
            )
            
            # Extract market sentiment
            market_sentiment = "neutral"
            volatility_level = "normal"
            
            if search_results:
                # Simple sentiment analysis based on search results
                positive_keywords = ["bullish", "surge", "rally", "gain", "up"]
                negative_keywords = ["bearish", "crash", "drop", "fall", "down"]
                
                text_content = " ".join([result.get("snippet", "") for result in search_results])
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text_content.lower())
                negative_count = sum(1 for keyword in negative_keywords if keyword in text_content.lower())
                
                if positive_count > negative_count:
                    market_sentiment = "bullish"
                elif negative_count > positive_count:
                    market_sentiment = "bearish"
            
            return {
                "sentiment": market_sentiment,
                "volatility": volatility_level,
                "news_count": len(search_results),
                "search_results": search_results
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market context: {e}")
            return {"sentiment": "unknown", "volatility": "unknown", "news_count": 0}
    
    async def _calculate_risk_score(self, opportunity: Dict, market_context: Dict) -> float:
        """Calculate risk score using AI analysis."""
        try:
            # Base risk factors
            risk_factors = {
                "profit_percentage": opportunity['profit_percentage'],
                "exchange_reliability": self._get_exchange_reliability(opportunity['buy_exchange'], opportunity['sell_exchange']),
                "market_sentiment": market_context.get('sentiment', 'unknown'),
                "volatility": market_context.get('volatility', 'unknown'),
                "confidence": opportunity['confidence']
            }
            
            # Use model optimizer to calculate risk
            risk_prompt = f"""
            Analyze this arbitrage opportunity and calculate a risk score from 0.0 (low risk) to 1.0 (high risk):
            
            Symbol: {opportunity['symbol']}
            Profit: {opportunity['profit_percentage']:.2%}
            Buy Exchange: {opportunity['buy_exchange']}
            Sell Exchange: {opportunity['sell_exchange']}
            Market Sentiment: {market_context.get('sentiment', 'unknown')}
            Confidence: {opportunity['confidence']:.2f}
            
            Consider factors like:
            - Exchange reliability and liquidity
            - Market volatility and sentiment
            - Execution risk and timing
            - Regulatory risks
            
            Return only a number between 0.0 and 1.0.
            """
            
            # For now, use a simple heuristic
            base_risk = 0.3  # Base risk for all arbitrage
            
            # Adjust based on profit (higher profit = higher risk)
            if opportunity['profit_percentage'] > 0.02:  # >2%
                base_risk += 0.2
            elif opportunity['profit_percentage'] > 0.01:  # >1%
                base_risk += 0.1
            
            # Adjust based on confidence
            base_risk -= (opportunity['confidence'] - 0.5) * 0.2
            
            # Adjust based on market sentiment
            if market_context.get('sentiment') == 'bearish':
                base_risk += 0.1
            elif market_context.get('sentiment') == 'bullish':
                base_risk -= 0.05
            
            return max(0.0, min(1.0, base_risk))
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 0.8  # Conservative high risk if calculation fails
    
    def _get_exchange_reliability(self, buy_exchange: str, sell_exchange: str) -> float:
        """Get reliability score for exchanges."""
        # Simple reliability scores (could be enhanced with real data)
        reliability_scores = {
            'binance': 0.9,
            'coinbase': 0.85,
            'kraken': 0.8,
            'coingecko': 0.7,  # aggregator, not exchange
        }
        
        buy_reliability = reliability_scores.get(buy_exchange, 0.5)
        sell_reliability = reliability_scores.get(sell_exchange, 0.5)
        
        return (buy_reliability + sell_reliability) / 2
    
    def _estimate_execution_time(self, opportunity: Dict) -> float:
        """Estimate execution time in seconds."""
        # Base execution time
        base_time = 10.0  # 10 seconds
        
        # Adjust based on exchanges
        exchange_speeds = {
            'binance': 1.0,
            'coinbase': 1.2,
            'kraken': 1.5,
            'coingecko': 2.0
        }
        
        buy_speed = exchange_speeds.get(opportunity['buy_exchange'], 1.5)
        sell_speed = exchange_speeds.get(opportunity['sell_exchange'], 1.5)
        
        return base_time * max(buy_speed, sell_speed)
    
    async def _record_failure(self, failure_type: str, error_message: str):
        """Record failure for analysis."""
        try:
            await self.root_cause_analyzer.record_failure(
                agent_type="crypto_arbitrage",
                objective="detect_arbitrage",
                error_message=error_message,
                failure_type=failure_type,
                context={
                    "total_scans": self.total_scans,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Error recording failure: {e}")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        return {
            "total_scans": self.total_scans,
            "successful_opportunities": len(self.successful_opportunities),
            "failed_opportunities": len(self.failed_opportunities),
            "success_rate": len(self.successful_opportunities) / max(1, self.total_scans),
            "average_profit": sum(opp.get('profit_percentage', 0) for opp in self.successful_opportunities) / max(1, len(self.successful_opportunities)),
            "last_scan": datetime.now().isoformat()
        }
    
    async def run_continuous_scan(self, interval_seconds: int = 60):
        """Run continuous arbitrage scanning."""
        self.logger.info(f"🚀 Starting continuous arbitrage scanning every {interval_seconds} seconds")
        
        while True:
            try:
                opportunities = await self.scan_for_opportunities()
                
                if opportunities:
                    self.logger.info(f"💰 Found {len(opportunities)} opportunities:")
                    for opp in opportunities[:3]:  # Show top 3
                        self.logger.info(f"  {opp.symbol}: {opp.profit_percentage:.2%} profit (Risk: {opp.risk_score:.2f})")
                
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️  Stopping continuous scan")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous scan: {e}")
                await asyncio.sleep(interval_seconds)

async def main():
    """Test the arbitrage detector."""
    logging.basicConfig(level=logging.INFO)
    
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
    
    # Run single scan
    opportunities = await detector.scan_for_opportunities()
    
    if opportunities:
        print(f"🎯 Found {len(opportunities)} viable opportunities:")
        for opp in opportunities:
            print(f"  {opp.symbol}: {opp.profit_percentage:.2%} profit")
            print(f"    Risk Score: {opp.risk_score:.2f}")
            print(f"    Execution Time: {opp.estimated_execution_time:.1f}s")
            print()
    else:
        print("❌ No viable arbitrage opportunities found")

if __name__ == "__main__":
    asyncio.run(main())