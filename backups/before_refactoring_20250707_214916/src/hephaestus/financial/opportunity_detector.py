"""
Main opportunity detection engine that coordinates all financial intelligence.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from hephaestus.financial.crypto_arbitrage import CryptoArbitrageDetector, ArbitrageOpportunity
from hephaestus.intelligence.knowledge_system import get_knowledge_system
from hephaestus.intelligence.model_optimizer import get_model_optimizer
from hephaestus.intelligence.self_awareness import get_self_awareness_core
from hephaestus.core.memory import Memory

@dataclass
class FinancialOpportunity:
    """Generic financial opportunity structure."""
    opportunity_type: str
    symbol: str
    description: str
    expected_profit: float
    risk_score: float
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            'opportunity_type': self.opportunity_type,
            'symbol': self.symbol,
            'description': self.description,
            'expected_profit': self.expected_profit,
            'risk_score': self.risk_score,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

class OpportunityDetector:
    """Main financial opportunity detection engine."""
    
    def __init__(self, config: Dict, logger: Optional[logging.Logger] = None, memory: Optional[Memory] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.memory = memory
        
        # Initialize specialized detectors
        self.crypto_arbitrage = CryptoArbitrageDetector(config, logger)
        
        # Initialize AI components
        self.knowledge_system = get_knowledge_system(config, logger)
        self.model_optimizer = get_model_optimizer(
            config.get('models', {}).get('opportunity_model', 'gpt-4'),
            logger
        )
        self.self_awareness = get_self_awareness_core(logger)
        
        # Opportunity settings
        self.min_confidence = config.get('opportunities', {}).get('min_confidence', 0.6)
        self.max_risk = config.get('opportunities', {}).get('max_risk', 0.8)
        self.scan_interval = config.get('opportunities', {}).get('scan_interval', 300)  # 5 minutes
        
        # Performance tracking
        self.detected_opportunities = []
        self.successful_executions = []
        self.total_profit = 0.0
        
    async def detect_all_opportunities(self) -> List[FinancialOpportunity]:
        """Detect all types of financial opportunities."""
        self.logger.info("🔍 Starting comprehensive opportunity detection")
        
        opportunities = []
        
        # 1. Crypto Arbitrage Opportunities
        arbitrage_opportunities = await self._detect_crypto_arbitrage()
        opportunities.extend(arbitrage_opportunities)
        
        # 2. DeFi Yield Opportunities (TODO)
        # defi_opportunities = await self._detect_defi_yields()
        # opportunities.extend(defi_opportunities)
        
        # 3. Market Trend Opportunities (TODO)
        # trend_opportunities = await self._detect_market_trends()
        # opportunities.extend(trend_opportunities)
        
        # 4. News-based Opportunities (TODO)
        # news_opportunities = await self._detect_news_based()
        # opportunities.extend(news_opportunities)
        
        # Filter and rank opportunities
        filtered_opportunities = self._filter_opportunities(opportunities)
        ranked_opportunities = self._rank_opportunities(filtered_opportunities)
        
        self.logger.info(f"📊 Found {len(ranked_opportunities)} viable opportunities")
        return ranked_opportunities
    
    async def _detect_crypto_arbitrage(self) -> List[FinancialOpportunity]:
        """Detect cryptocurrency arbitrage opportunities."""
        try:
            arbitrage_opportunities = await self.crypto_arbitrage.scan_for_opportunities()
            
            financial_opportunities = []
            for arb_opp in arbitrage_opportunities:
                financial_opp = FinancialOpportunity(
                    opportunity_type="crypto_arbitrage",
                    symbol=arb_opp.symbol,
                    description=f"Arbitrage {arb_opp.symbol} between {arb_opp.buy_exchange} and {arb_opp.sell_exchange}",
                    expected_profit=arb_opp.profit_percentage,
                    risk_score=arb_opp.risk_score,
                    confidence=arb_opp.confidence,
                    timestamp=arb_opp.timestamp,
                    metadata={
                        'buy_exchange': arb_opp.buy_exchange,
                        'sell_exchange': arb_opp.sell_exchange,
                        'buy_price': arb_opp.buy_price,
                        'sell_price': arb_opp.sell_price,
                        'profit_amount': arb_opp.profit_amount,
                        'execution_time': arb_opp.estimated_execution_time
                    }
                )
                financial_opportunities.append(financial_opp)
            
            return financial_opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting crypto arbitrage: {e}")
            return []
    
    async def _detect_defi_yields(self) -> List[FinancialOpportunity]:
        """Detect DeFi yield farming opportunities."""
        # TODO: Implement DeFi yield detection
        try:
            # Use knowledge system to research current DeFi protocols
            search_query = "DeFi yield farming highest APY 2024 liquidity pools"
            
            search_results = await self.knowledge_system.intelligent_search(
                search_query,
                search_type="defi_research",
                max_results=10
            )
            
            # Process results and extract yield opportunities
            opportunities = []
            
            # This is a placeholder - would need actual DeFi protocol integration
            if search_results:
                self.logger.info(f"Found {len(search_results)} DeFi research results")
                
                # Example opportunity (would be extracted from real data)
                opportunities.append(FinancialOpportunity(
                    opportunity_type="defi_yield",
                    symbol="USDC-ETH",
                    description="Uniswap V3 liquidity provision",
                    expected_profit=0.15,  # 15% APY
                    risk_score=0.4,
                    confidence=0.7,
                    timestamp=datetime.now(),
                    metadata={
                        'protocol': 'uniswap_v3',
                        'pool': 'USDC-ETH',
                        'apy': 0.15,
                        'tvl': 100000000,  # $100M TVL
                        'impermanent_loss_risk': 0.3
                    }
                ))
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting DeFi yields: {e}")
            return []
    
    async def _detect_market_trends(self) -> List[FinancialOpportunity]:
        """Detect market trend-based opportunities."""
        # TODO: Implement trend detection
        try:
            # Use knowledge system to research market trends
            search_query = "cryptocurrency market trends bullish signals 2024"
            
            search_results = await self.knowledge_system.intelligent_search(
                search_query,
                search_type="trend_analysis",
                max_results=10
            )
            
            opportunities = []
            
            # Process search results for trend opportunities
            if search_results:
                self.logger.info(f"Found {len(search_results)} trend analysis results")
                
                # Example trend opportunity
                opportunities.append(FinancialOpportunity(
                    opportunity_type="trend_following",
                    symbol="BTC/USD",
                    description="Bitcoin bullish trend continuation",
                    expected_profit=0.08,  # 8% expected return
                    risk_score=0.6,
                    confidence=0.65,
                    timestamp=datetime.now(),
                    metadata={
                        'trend_direction': 'bullish',
                        'trend_strength': 0.7,
                        'support_level': 45000,
                        'resistance_level': 52000,
                        'entry_price': 47000
                    }
                ))
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting market trends: {e}")
            return []
    
    def _filter_opportunities(self, opportunities: List[FinancialOpportunity]) -> List[FinancialOpportunity]:
        """Filter opportunities based on risk and confidence criteria."""
        filtered = []
        
        for opp in opportunities:
            # Check minimum confidence
            if opp.confidence < self.min_confidence:
                self.logger.debug(f"Filtered out {opp.symbol} due to low confidence: {opp.confidence}")
                continue
            
            # Check maximum risk
            if opp.risk_score > self.max_risk:
                self.logger.debug(f"Filtered out {opp.symbol} due to high risk: {opp.risk_score}")
                continue
            
            # Check for duplicate or similar opportunities
            if not self._is_duplicate_opportunity(opp, filtered):
                filtered.append(opp)
        
        return filtered
    
    def _is_duplicate_opportunity(self, opp: FinancialOpportunity, existing: List[FinancialOpportunity]) -> bool:
        """Check if opportunity is duplicate or very similar to existing ones."""
        for existing_opp in existing:
            if (opp.opportunity_type == existing_opp.opportunity_type and 
                opp.symbol == existing_opp.symbol and
                abs(opp.expected_profit - existing_opp.expected_profit) < 0.01):  # 1% difference
                return True
        return False
    
    def _rank_opportunities(self, opportunities: List[FinancialOpportunity]) -> List[FinancialOpportunity]:
        """Rank opportunities by expected value (profit * confidence / risk)."""
        def calculate_score(opp: FinancialOpportunity) -> float:
            # Expected value calculation
            return (opp.expected_profit * opp.confidence) / max(opp.risk_score, 0.1)
        
        return sorted(opportunities, key=calculate_score, reverse=True)
    
    async def execute_opportunity(self, opportunity: FinancialOpportunity) -> Dict[str, Any]:
        """Execute a financial opportunity (placeholder for actual execution)."""
        self.logger.info(f"🚀 Executing opportunity: {opportunity.description}")
        
        # This would contain actual execution logic
        # For now, it's a simulation
        
        execution_result = {
            'opportunity_id': f"{opportunity.opportunity_type}_{opportunity.symbol}_{int(opportunity.timestamp.timestamp())}",
            'status': 'simulated',
            'executed_at': datetime.now(),
            'expected_profit': opportunity.expected_profit,
            'actual_profit': 0.0,  # Would be calculated after execution
            'execution_time': 0.0,
            'notes': 'Simulated execution - actual trading not implemented'
        }
        
        # Store in memory if available
        if self.memory:
            self.memory.add_successful_objective(
                f"Execute {opportunity.opportunity_type}",
                execution_result
            )
        
        return execution_result
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of opportunity detection."""
        return {
            'total_opportunities_detected': len(self.detected_opportunities),
            'successful_executions': len(self.successful_executions),
            'total_profit': self.total_profit,
            'average_profit_per_opportunity': self.total_profit / max(1, len(self.successful_executions)),
            'success_rate': len(self.successful_executions) / max(1, len(self.detected_opportunities)),
            'last_scan': datetime.now().isoformat(),
            'crypto_arbitrage_performance': self.crypto_arbitrage.get_performance_summary()
        }
    
    async def run_continuous_detection(self, interval_seconds: Optional[int] = None):
        """Run continuous opportunity detection."""
        if interval_seconds is None:
            interval_seconds = self.scan_interval
        
        self.logger.info(f"🎯 Starting continuous opportunity detection every {interval_seconds} seconds")
        
        while True:
            try:
                opportunities = await self.detect_all_opportunities()
                
                if opportunities:
                    self.logger.info(f"💰 TOP OPPORTUNITIES:")
                    for i, opp in enumerate(opportunities[:5], 1):
                        score = (opp.expected_profit * opp.confidence) / max(opp.risk_score, 0.1)
                        self.logger.info(f"  {i}. {opp.description}")
                        self.logger.info(f"     Expected Profit: {opp.expected_profit:.2%}")
                        self.logger.info(f"     Risk Score: {opp.risk_score:.2f}")
                        self.logger.info(f"     Confidence: {opp.confidence:.2f}")
                        self.logger.info(f"     Score: {score:.2f}")
                        self.logger.info("")
                
                self.detected_opportunities.extend(opportunities)
                
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️  Stopping continuous detection")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous detection: {e}")
                await asyncio.sleep(interval_seconds)

async def main():
    """Test the opportunity detector."""
    logging.basicConfig(level=logging.INFO)
    
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
    
    # Run single detection
    opportunities = await detector.detect_all_opportunities()
    
    if opportunities:
        print(f"🎯 Found {len(opportunities)} opportunities:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp.description}")
            print(f"     Expected Profit: {opp.expected_profit:.2%}")
            print(f"     Risk: {opp.risk_score:.2f} | Confidence: {opp.confidence:.2f}")
            print()
    else:
        print("❌ No opportunities found")

if __name__ == "__main__":
    asyncio.run(main())