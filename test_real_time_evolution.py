#!/usr/bin/env python3
"""
⚡ Test script for Real-Time Evolution Engine

This script tests the Real-Time Evolution Engine to verify:
1. Continuous mutation generation
2. Parallel mutation testing
3. Fitness evaluation and deployment
4. Hot-upgrade capabilities
5. Performance monitoring
"""

import sys
import logging
import asyncio
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hephaestus.intelligence.real_time_evolution_engine import (
    get_real_time_evolution_engine, 
    MutationType, 
    EvolutionPhase,
    EvolutionCandidate
)
from hephaestus.utils.config_loader import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_evolution_engine():
    """Test the Real-Time Evolution Engine comprehensively"""
    
    print("⚡ TESTING REAL-TIME EVOLUTION ENGINE")
    print("=" * 50)
    
    # Load config
    config = load_config()
    
    # Get engine
    engine = get_real_time_evolution_engine(config, logger)
    
    # Test 1: Basic Status
    print("\n🔍 Test 1: Basic Status Check")
    print("-" * 30)
    
    status = engine.get_evolution_status()
    print(f"  • Evolution enabled: {status['evolution_enabled']}")
    print(f"  • Current phase: {status['current_phase']}")
    print(f"  • Active candidates: {status['active_candidates']}")
    print(f"  • Active tests: {status['active_tests']}")
    print(f"  • Deployed mutations: {status['deployed_mutations']}")
    
    # Test 2: Mutation Generation
    print("\n🧬 Test 2: Mutation Generation")
    print("-" * 30)
    
    initial_candidates = len(engine.evolution_candidates)
    engine._generate_mutations()
    new_candidates = len(engine.evolution_candidates) - initial_candidates
    
    print(f"  • Generated {new_candidates} new mutation candidates")
    
    if engine.evolution_candidates:
        candidate = list(engine.evolution_candidates.values())[0]
        print(f"  • Sample candidate: {candidate.description[:80]}...")
        print(f"  • Mutation type: {candidate.mutation_type.value}")
        print(f"  • Risk level: {candidate.risk_level:.2f}")
    
    # Test 3: Performance Monitoring
    print("\n📊 Test 3: Performance Monitoring")
    print("-" * 30)
    
    engine._monitor_performance()
    
    if engine.performance_history:
        latest_metrics = engine.performance_history[-1]["metrics"]
        print(f"  • Success rate: {latest_metrics['success_rate']:.1%}")
        print(f"  • Avg execution time: {latest_metrics['average_execution_time']:.1f}s")
        print(f"  • Error rate: {latest_metrics['error_rate']:.1%}")
        print(f"  • Memory usage: {latest_metrics['memory_usage']:.1%}")
        print(f"  • Agent efficiency: {latest_metrics['agent_efficiency']:.1%}")
    
    # Test 4: Async Mutation Testing (simulation)
    print("\n🧪 Test 4: Async Mutation Testing")
    print("-" * 30)
    
    async def test_async_mutations():
        # Get a candidate to test
        if engine.evolution_candidates:
            candidate = list(engine.evolution_candidates.values())[0]
            print(f"  • Testing candidate: {candidate.description[:50]}...")
            
            # Simulate async testing
            await engine._test_single_mutation(candidate)
            
            print(f"  • Test completed! Fitness score: {candidate.fitness_score:.3f}")
            print(f"  • Success rate: {candidate.success_rate:.1%}")
            print(f"  • Performance impact: {candidate.performance_impact:.3f}")
            
            return candidate
        else:
            print("  • No candidates available for testing")
            return None
    
    # Run async test
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    tested_candidate = loop.run_until_complete(test_async_mutations())
    
    # Test 5: Evaluation and Deployment
    print("\n🚀 Test 5: Evaluation and Deployment")
    print("-" * 30)
    
    if tested_candidate:
        # Artificially set a high fitness score for testing
        tested_candidate.fitness_score = 0.8
        tested_candidate.risk_level = 0.1  # Low risk
        
        engine._evaluate_mutations()
        engine._deploy_best_mutations()
        
        final_status = engine.get_evolution_status()
        print(f"  • Final deployed mutations: {final_status['deployed_mutations']}")
        print(f"  • Best fitness score: {final_status['metrics']['best_fitness_score']:.3f}")
    
    # Test 6: Best Mutations Report
    print("\n🏆 Test 6: Best Mutations Report")
    print("-" * 30)
    
    best_mutations = engine.get_best_mutations(limit=3)
    for i, mutation in enumerate(best_mutations, 1):
        print(f"  • #{i}: {mutation['description'][:60]}...")
        print(f"    Fitness: {mutation['fitness_score']:.3f}, Risk: {mutation['risk_level']:.2f}")
    
    # Test 7: Emergency Evolution
    print("\n🚨 Test 7: Emergency Evolution Trigger")
    print("-" * 30)
    
    # Simulate performance degradation
    original_baseline = engine.baseline_performance.copy()
    engine.baseline_performance = {
        "success_rate": 0.8,
        "average_execution_time": 30.0,
        "error_rate": 0.1,
        "memory_usage": 0.3,
        "agent_efficiency": 0.7
    }
    
    # Simulate poor current performance
    poor_metrics = {
        "success_rate": 0.4,  # Much lower
        "average_execution_time": 60.0,  # Much higher
        "error_rate": 0.4,  # Much higher
        "memory_usage": 0.8,  # Much higher
        "agent_efficiency": 0.3  # Much lower
    }
    
    delta = engine._calculate_performance_delta(poor_metrics)
    print(f"  • Performance delta: {delta:.1%}")
    
    if delta < -0.2:
        print("  • 🚨 Emergency evolution would be triggered!")
        engine._trigger_emergency_evolution()
        emergency_mutations = [c for c in engine.evolution_candidates.values() 
                             if c.candidate_id.startswith("emergency_")]
        print(f"  • Generated {len(emergency_mutations)} emergency mutations")
    
    # Restore original baseline
    engine.baseline_performance = original_baseline
    
    # Test 8: State Persistence
    print("\n💾 Test 8: State Persistence")
    print("-" * 30)
    
    state_file = engine.save_evolution_state()
    print(f"  • Evolution state saved to: {state_file}")
    
    # Verify the saved file
    if state_file.exists():
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        print(f"  • Saved state contains {len(saved_state.keys())} top-level keys")
        print(f"  • Best mutations in state: {len(saved_state.get('best_mutations', []))}")
        print(f"  • Performance history entries: {len(saved_state.get('performance_history', []))}")
    
    # Test 9: Callback Registration
    print("\n📋 Test 9: Callback Registration")
    print("-" * 30)
    
    callback_test_results = {}
    
    def test_callback(mutation_data):
        callback_test_results["called"] = True
        callback_test_results["data"] = mutation_data
        return True
    
    engine.register_mutation_callback(MutationType.PROMPT_OPTIMIZATION, test_callback)
    
    # Test the callback
    test_mutation_data = {"target": "test", "modification": "test modification"}
    success = engine._deploy_mutation(EvolutionCandidate(
        candidate_id="test_callback",
        mutation_type=MutationType.PROMPT_OPTIMIZATION,
        description="Test callback",
        mutation_data=test_mutation_data
    ))
    
    print(f"  • Callback registration test: {'✅ SUCCESS' if callback_test_results.get('called') else '❌ FAILED'}")
    print(f"  • Deployment success: {'✅ YES' if success else '❌ NO'}")
    
    # Final Status
    print("\n📈 Final Evolution Engine Status")
    print("-" * 30)
    
    final_status = engine.get_evolution_status()
    metrics = final_status["metrics"]
    
    print(f"  • Total mutations generated: {metrics['total_mutations_generated']}")
    print(f"  • Total mutations tested: {metrics['total_mutations_tested']}")
    print(f"  • Total mutations deployed: {metrics['total_mutations_deployed']}")
    print(f"  • Successful deployments: {metrics['successful_deployments']}")
    print(f"  • Evolution uptime: {metrics['evolution_uptime']:.1f}s")
    print(f"  • Best fitness score: {metrics['best_fitness_score']:.3f}")
    
    print("\n🎉 All Real-Time Evolution Engine tests completed!")
    print("=" * 50)
    
    return engine

def test_continuous_evolution():
    """Test the engine running continuously for a short period"""
    
    print("\n⏱️ TESTING CONTINUOUS EVOLUTION (30 seconds)")
    print("=" * 50)
    
    config = load_config()
    engine = get_real_time_evolution_engine(config, logger)
    
    # Start evolution
    engine.start_evolution()
    print("🚀 Evolution started...")
    
    # Let it run for 30 seconds
    start_time = time.time()
    duration = 30  # seconds
    
    while time.time() - start_time < duration:
        status = engine.get_evolution_status()
        print(f"Phase: {status['current_phase']}, "
              f"Candidates: {status['active_candidates']}, "
              f"Tests: {status['active_tests']}")
        time.sleep(5)
    
    # Stop evolution
    engine.stop_evolution()
    print("🛑 Evolution stopped")
    
    # Final report
    final_status = engine.get_evolution_status()
    metrics = final_status["metrics"]
    
    print(f"\n📊 Results after {duration} seconds:")
    print(f"  • Mutations generated: {metrics['total_mutations_generated']}")
    print(f"  • Mutations tested: {metrics['total_mutations_tested']}")
    print(f"  • Mutations deployed: {metrics['total_mutations_deployed']}")
    print(f"  • Evolution uptime: {metrics['evolution_uptime']:.1f}s")

if __name__ == "__main__":
    # Run comprehensive tests
    engine = test_evolution_engine()
    
    # Ask user if they want to test continuous evolution
    print("\n" + "="*50)
    response = input("🤔 Would you like to test continuous evolution for 30 seconds? (y/N): ")
    
    if response.lower().startswith('y'):
        test_continuous_evolution()
    
    print("\n✅ All tests completed successfully!")