#!/usr/bin/env python3
"""
🔮 Test script for Predictive Failure Engine

This script tests the Predictive Failure Engine to see if it can:
1. Predict failures correctly
2. Modify objectives preventively
3. Learn from feedback
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hephaestus.intelligence.predictive_failure_engine import get_predictive_failure_engine
from hephaestus.monitoring.predictive_failure_dashboard import get_predictive_failure_dashboard
from hephaestus.utils.config_loader import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_predictive_engine():
    """Test the Predictive Failure Engine"""
    
    print("🔮 TESTING PREDICTIVE FAILURE ENGINE")
    print("=" * 50)
    
    # Load config
    config = load_config()
    memory_path = "data/memory/HEPHAESTUS_MEMORY.json"
    
    # Get engine
    engine = get_predictive_failure_engine(config, logger, memory_path)
    
    # Test objectives (some should trigger high failure probability)
    test_objectives = [
        # High risk objective (complex async refactor)
        """Refactor the `src/hephaestus/api/rest/main.py` module (LOC: 2796) by splitting it into smaller, focused modules (e.g., `api_handlers.py`, `status_management.py`, `evolution_triggers.py`) to reduce complexity and improve maintainability, ensuring proper error handling for async operations to prevent failures like the previous `ASYNC_PIPELINE_ERROR`.""",
        
        # Medium risk objective (complex but no async)
        """Implement a new feature to analyze code metrics and generate detailed reports about code quality, complexity, and maintainability for the entire codebase.""",
        
        # Low risk objective (simple task)
        """Add a new configuration option to enable/disable debug logging in the system.""",
        
        # High risk objective (known failure pattern)
        """Refactor the MaestroAgent's core decision-making logic to implement dynamic strategy weighting based on historical performance metrics, focusing on improving its current success rate."""
    ]
    
    print("\n🎯 Testing Failure Predictions:")
    print("-" * 30)
    
    for i, objective in enumerate(test_objectives, 1):
        print(f"\n📋 Test {i}: {objective[:80]}...")
        
        # Predict failure
        analysis = engine.predict_failure_probability(objective)
        
        print(f"  🔮 Failure Probability: {analysis.failure_probability:.1%}")
        print(f"  🎯 Confidence Level: {analysis.confidence_level:.1%}")
        print(f"  ⚠️ Risk Factors: {len(analysis.risk_factors)}")
        
        if analysis.risk_factors:
            for risk in analysis.risk_factors[:3]:  # Show top 3
                print(f"    • {risk}")
        
        # Check if modifications would be applied
        if engine.should_modify_objective(analysis):
            print(f"  🛡️ Would apply {len(analysis.recommended_modifications)} modifications")
            modified = engine.apply_preventive_modifications(objective, analysis)
            print(f"  📝 Modified length: {len(modified)} chars (original: {len(objective)})")
        else:
            print(f"  ✅ No modifications needed")
    
    # Test learning
    print("\n🎓 Testing Learning:")
    print("-" * 20)
    
    # Simulate some failures for learning
    engine.learn_from_execution(
        objective=test_objectives[0],
        success=False,
        failure_reason="ASYNC_PIPELINE_ERROR",
        execution_time=45.2
    )
    
    engine.learn_from_execution(
        objective=test_objectives[2],
        success=True,
        execution_time=12.1
    )
    
    print("  📚 Simulated learning from 2 executions")
    
    # Test dashboard
    print("\n📊 Testing Dashboard:")
    print("-" * 20)
    
    dashboard = get_predictive_failure_dashboard(config, logger, memory_path)
    report = dashboard.get_comprehensive_report()
    
    print(f"  • Total Patterns: {report['engine_status']['total_patterns']}")
    print(f"  • Prediction History: {report['engine_status']['prediction_history_size']}")
    print(f"  • Accuracy: {report['accuracy_metrics']['accuracy']:.1%}")
    
    # Show some dangerous patterns
    dangerous = report['failure_patterns']['most_dangerous_patterns']
    if dangerous:
        print(f"  • Most Dangerous Pattern: {dangerous[0]['pattern_id']}")
        print(f"    Failure Prob: {dangerous[0]['failure_probability']:.1%}")
    
    print("\n🎉 All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_predictive_engine()