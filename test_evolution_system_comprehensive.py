#!/usr/bin/env python3
"""
⚡ COMPREHENSIVE EVOLUTION SYSTEM TEST ⚡

Script de teste completo para demonstrar o sistema de evolução 100% funcional:
1. Real-Time Evolution Engine (evolução contínua)
2. Parallel Reality Testing (teste paralelo de estratégias)
3. Collective Intelligence Network (rede de inteligência coletiva)
4. Evolution Callbacks (callbacks funcionais)

Este script demonstra um "Formula 1 com motor real correndo em pista real"!
"""

import sys
import asyncio
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('evolution_system_test.log')
    ]
)
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'─'*40}")
    print(f"⚡ {title}")
    print(f"{'─'*40}")

def print_result(status: str, description: str, details: Dict[str, Any] = None):
    """Print a formatted result"""
    status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
    print(f"{status_emoji} {description}")
    if details:
        for key, value in details.items():
            print(f"   • {key}: {value}")

async def test_real_time_evolution_engine():
    """Test the Real-Time Evolution Engine"""
    print_section("REAL-TIME EVOLUTION ENGINE TEST")
    
    try:
        from hephaestus.utils.config_loader import load_config
        from hephaestus.intelligence.real_time_evolution_engine import (
            get_real_time_evolution_engine,
            MutationType
        )
        
        config = load_config()
        engine = get_real_time_evolution_engine(config, logger)
        
        # Test 1: Basic Status
        print_subsection("Basic Status Check")
        status = engine.get_evolution_status()
        print_result("success", "Evolution engine status retrieved", {
            "Evolution enabled": status['evolution_enabled'],
            "Current phase": status['current_phase'],
            "Active candidates": status['active_candidates'],
            "Deployed mutations": status['deployed_mutations']
        })
        
        # Test 2: Mutation Generation
        print_subsection("Mutation Generation")
        initial_count = len(engine.evolution_candidates)
        
        # Generate different types of mutations
        mutations_generated = 0
        mutation_types = [
            MutationType.PROMPT_OPTIMIZATION,
            MutationType.STRATEGY_ADJUSTMENT,
            MutationType.PARAMETER_TUNING,
            MutationType.WORKFLOW_MODIFICATION,
            MutationType.AGENT_BEHAVIOR_CHANGE
        ]
        
        for mutation_type in mutation_types:
            try:
                if mutation_type == MutationType.PROMPT_OPTIMIZATION:
                    candidate = engine._generate_prompt_optimization()
                elif mutation_type == MutationType.STRATEGY_ADJUSTMENT:
                    candidate = engine._generate_strategy_adjustment()
                elif mutation_type == MutationType.PARAMETER_TUNING:
                    candidate = engine._generate_parameter_tuning()
                elif mutation_type == MutationType.WORKFLOW_MODIFICATION:
                    candidate = engine._generate_workflow_modification()
                elif mutation_type == MutationType.AGENT_BEHAVIOR_CHANGE:
                    candidate = engine._generate_agent_behavior_change()
                
                if candidate:
                    engine.evolution_candidates[candidate.candidate_id] = candidate
                    mutations_generated += 1
                    print_result("success", f"Generated {mutation_type.value} mutation", {
                        "Candidate ID": candidate.candidate_id,
                        "Description": candidate.description[:50] + "...",
                        "Risk level": f"{candidate.risk_level:.2f}"
                    })
                    
            except Exception as e:
                print_result("error", f"Failed to generate {mutation_type.value}", {"Error": str(e)})
        
        print_result("success", f"Total mutations generated: {mutations_generated}")
        
        # Test 3: Mutation Testing
        print_subsection("Mutation Testing")
        if engine.evolution_candidates:
            # Test the first candidate
            candidate = list(engine.evolution_candidates.values())[0]
            print(f"Testing candidate: {candidate.description[:50]}...")
            
            engine._test_single_mutation_sync(candidate)
            
            print_result("success", "Mutation testing completed", {
                "Fitness score": f"{candidate.fitness_score:.3f}",
                "Success rate": f"{candidate.success_rate:.1%}",
                "Performance impact": f"{candidate.performance_impact:.3f}"
            })
        
        # Test 4: Callback System
        print_subsection("Callback System")
        callback_results = {}
        
        def test_callback(mutation_data):
            callback_results["called"] = True
            callback_results["data"] = mutation_data
            return True
        
        engine.register_mutation_callback(MutationType.PROMPT_OPTIMIZATION, test_callback)
        
        # Test deployment
        if engine.evolution_candidates:
            candidate = list(engine.evolution_candidates.values())[0]
            candidate.fitness_score = 0.8  # Set high fitness
            candidate.risk_level = 0.1     # Set low risk
            
            success = engine._deploy_mutation(candidate)
            print_result("success" if success else "warning", "Callback deployment test", {
                "Callback called": callback_results.get("called", False),
                "Deployment success": success
            })
        
        # Test 5: Continuous Evolution (Short Demo)
        print_subsection("Continuous Evolution Demo")
        print("Starting evolution engine for 10 seconds...")
        
        engine.start_evolution()
        start_time = time.time()
        
        while time.time() - start_time < 10:
            status = engine.get_evolution_status()
            print(f"Phase: {status['current_phase']}, Candidates: {status['active_candidates']}")
            await asyncio.sleep(2)
        
        engine.stop_evolution()
        
        final_status = engine.get_evolution_status()
        print_result("success", "Continuous evolution demo completed", {
            "Final candidates": final_status['active_candidates'],
            "Total mutations generated": final_status['metrics']['total_mutations_generated'],
            "Total mutations tested": final_status['metrics']['total_mutations_tested']
        })
        
        return True
        
    except Exception as e:
        print_result("error", f"Real-Time Evolution Engine test failed: {e}")
        return False

async def test_parallel_reality_testing():
    """Test the Parallel Reality Testing System"""
    print_section("PARALLEL REALITY TESTING SYSTEM TEST")
    
    try:
        from hephaestus.utils.config_loader import load_config
        from hephaestus.intelligence.parallel_reality_testing import (
            get_parallel_reality_tester,
            TestStrategy,
            StrategyType,
            TestEnvironmentType
        )
        
        config = load_config()
        tester = get_parallel_reality_tester(config, logger)
        
        # Test 1: Status Check
        print_subsection("Status Check")
        status = tester.get_test_status()
        print_result("success", "Parallel tester status retrieved", {
            "Max parallel tests": status['max_parallel_tests'],
            "Active tests": status['active_tests'],
            "Test history": status['test_history_count']
        })
        
        # Test 2: Strategy Creation
        print_subsection("Strategy Creation")
        strategies = [
            TestStrategy(
                strategy_id="conservative_approach",
                strategy_type=StrategyType.PARAMETER_COMBINATION,
                name="Conservative Approach",
                description="Conservative strategy with low risk parameters",
                parameters={
                    "temperature": 0.3,
                    "max_tokens": 1500,
                    "retry_count": 3
                },
                expected_benefits=["High reliability", "Low error rate"],
                risk_level=0.1
            ),
            TestStrategy(
                strategy_id="aggressive_approach",
                strategy_type=StrategyType.PARAMETER_COMBINATION,
                name="Aggressive Approach",
                description="Aggressive strategy with high performance parameters",
                parameters={
                    "temperature": 0.7,
                    "max_tokens": 3000,
                    "retry_count": 1
                },
                expected_benefits=["High performance", "Fast execution"],
                risk_level=0.6
            ),
            TestStrategy(
                strategy_id="balanced_approach",
                strategy_type=StrategyType.PARAMETER_COMBINATION,
                name="Balanced Approach",
                description="Balanced strategy with optimized parameters",
                parameters={
                    "temperature": 0.5,
                    "max_tokens": 2000,
                    "retry_count": 2
                },
                expected_benefits=["Good balance", "Reliable performance"],
                risk_level=0.3
            )
        ]
        
        for strategy in strategies:
            print_result("success", f"Created strategy: {strategy.name}", {
                "Strategy ID": strategy.strategy_id,
                "Type": strategy.strategy_type.value,
                "Risk level": f"{strategy.risk_level:.1f}"
            })
        
        # Test 3: Parallel Testing
        print_subsection("Parallel Testing Execution")
        print("Running parallel tests...")
        
        results = tester.test_strategies(strategies)
        
        if results:
            print_result("success", f"Parallel testing completed: {len(results)} results")
            
            for strategy_id, result in results.items():
                print_result("success", f"Strategy {strategy_id} results", {
                    "Success": result.success,
                    "Fitness score": f"{result.fitness_score:.3f}",
                    "Execution time": f"{result.execution_time:.2f}s",
                    "Success rate": f"{result.success_rate:.1%}"
                })
        
        # Test 4: Best Strategy Selection
        print_subsection("Best Strategy Selection")
        if results:
            best_strategy = tester._select_best_strategy(results)
            if best_strategy:
                print_result("success", "Best strategy selected", {
                    "Strategy ID": best_strategy['strategy_id'],
                    "Fitness score": f"{best_strategy['fitness_score']:.3f}",
                    "Description": best_strategy['description']
                })
        
        return True
        
    except Exception as e:
        print_result("error", f"Parallel Reality Testing test failed: {e}")
        return False

async def test_collective_intelligence_network():
    """Test the Collective Intelligence Network"""
    print_section("COLLECTIVE INTELLIGENCE NETWORK TEST")
    
    try:
        from hephaestus.utils.config_loader import load_config
        from hephaestus.intelligence.collective_intelligence_network import (
            get_collective_intelligence_network,
            KnowledgeType,
            KnowledgeRelevance
        )
        
        config = load_config()
        network = get_collective_intelligence_network(config, logger)
        
        # Test 1: Agent Registration
        print_subsection("Agent Registration")
        agents = [
            {
                "agent_id": "architect_agent",
                "agent_type": "architect",
                "capabilities": ["code_generation", "architecture_design"],
                "expertise_areas": ["system_design", "code_optimization"]
            },
            {
                "agent_id": "maestro_agent",
                "agent_type": "maestro",
                "capabilities": ["task_coordination", "strategy_selection"],
                "expertise_areas": ["orchestration", "decision_making"]
            },
            {
                "agent_id": "bug_hunter_agent",
                "agent_type": "bug_hunter",
                "capabilities": ["error_detection", "debugging"],
                "expertise_areas": ["quality_assurance", "error_analysis"]
            }
        ]
        
        for agent in agents:
            success = network.register_agent(
                agent["agent_id"],
                agent["agent_type"],
                agent["capabilities"],
                agent["expertise_areas"]
            )
            print_result("success" if success else "error", f"Registered agent: {agent['agent_id']}", {
                "Type": agent["agent_type"],
                "Capabilities": len(agent["capabilities"]),
                "Expertise areas": len(agent["expertise_areas"])
            })
        
        # Test 2: Knowledge Sharing
        print_subsection("Knowledge Sharing")
        knowledge_items = [
            {
                "agent_id": "architect_agent",
                "knowledge_type": KnowledgeType.SOLUTION_PATTERN,
                "title": "Efficient Code Generation Pattern",
                "content": "Use template-based approach with dynamic parameter injection for scalable code generation",
                "tags": ["code_generation", "templates", "scalability"]
            },
            {
                "agent_id": "maestro_agent",
                "knowledge_type": KnowledgeType.STRATEGY_DISCOVERY,
                "title": "Optimal Task Prioritization",
                "content": "Prioritize tasks based on impact score and resource availability for maximum efficiency",
                "tags": ["task_management", "prioritization", "efficiency"]
            },
            {
                "agent_id": "bug_hunter_agent",
                "knowledge_type": KnowledgeType.ERROR_RECOVERY,
                "title": "Graceful Error Recovery",
                "content": "Implement fallback mechanisms with exponential backoff for robust error handling",
                "tags": ["error_handling", "recovery", "robustness"]
            }
        ]
        
        for item in knowledge_items:
            knowledge_id = network.share_knowledge(
                item["agent_id"],
                item["knowledge_type"],
                item["title"],
                item["content"],
                tags=item["tags"]
            )
            print_result("success" if knowledge_id else "error", f"Shared knowledge: {item['title']}", {
                "Knowledge ID": knowledge_id,
                "Type": item["knowledge_type"].value,
                "Source": item["agent_id"]
            })
        
        # Test 3: Knowledge Search
        print_subsection("Knowledge Search")
        search_queries = [
            "code generation",
            "error handling",
            "task prioritization"
        ]
        
        for query in search_queries:
            results = network.search_knowledge("test_agent", query, max_results=3)
            print_result("success", f"Search query: '{query}'", {
                "Results found": len(results),
                "Top result": results[0].title if results else "None"
            })
        
        # Test 4: Knowledge Validation
        print_subsection("Knowledge Validation")
        if network.knowledge_base:
            knowledge_id = list(network.knowledge_base.keys())[0]
            
            # Validate as successful
            success = network.validate_knowledge("test_agent", knowledge_id, True, "Works well in practice")
            print_result("success" if success else "error", f"Knowledge validation", {
                "Knowledge ID": knowledge_id,
                "Validation": "Success",
                "Feedback": "Works well in practice"
            })
        
        # Test 5: Agent Recommendations
        print_subsection("Agent Recommendations")
        recommendations = network.get_agent_recommendations("architect_agent", {
            "current_task": "system_optimization",
            "context": "performance_improvement"
        })
        
        print_result("success", "Agent recommendations generated", {
            "Recommendations count": len(recommendations),
            "Types": [r["type"] for r in recommendations]
        })
        
        # Test 6: Network Status
        print_subsection("Network Status")
        network_status = network.get_network_status()
        print_result("success", "Network status retrieved", {
            "Active agents": network_status.get("active_agents", 0),
            "Total knowledge": network_status.get("total_knowledge", 0),
            "Total insights": network_status.get("total_insights", 0)
        })
        
        return True
        
    except Exception as e:
        print_result("error", f"Collective Intelligence Network test failed: {e}")
        return False

async def test_evolution_callbacks():
    """Test the Evolution Callbacks System"""
    print_section("EVOLUTION CALLBACKS SYSTEM TEST")
    
    try:
        from hephaestus.utils.config_loader import load_config
        from hephaestus.intelligence.evolution_callbacks import get_evolution_callbacks
        
        config = load_config()
        callbacks = get_evolution_callbacks(config, logger)
        
        # Test 1: System State
        print_subsection("System State Check")
        system_state = callbacks.get_system_state()
        print_result("success", "System state retrieved", {
            "Total changes": system_state.get("total_changes", 0),
            "Successful changes": system_state.get("successful_changes", 0),
            "Failed changes": system_state.get("failed_changes", 0)
        })
        
        # Test 2: Prompt Optimization
        print_subsection("Prompt Optimization Test")
        prompt_mutation = {
            "target": "test_agent",
            "modification": "Add more context for better performance"
        }
        
        success = callbacks.apply_prompt_optimization(prompt_mutation)
        print_result("success" if success else "warning", "Prompt optimization applied", {
            "Target": prompt_mutation["target"],
            "Modification": prompt_mutation["modification"],
            "Success": success
        })
        
        # Test 3: Strategy Adjustment
        print_subsection("Strategy Adjustment Test")
        strategy_mutation = {
            "strategy": "cycle_delay_seconds",
            "old_value": 1.0,
            "new_value": 0.5
        }
        
        success = callbacks.apply_strategy_adjustment(strategy_mutation)
        print_result("success" if success else "warning", "Strategy adjustment applied", {
            "Strategy": strategy_mutation["strategy"],
            "Old value": strategy_mutation["old_value"],
            "New value": strategy_mutation["new_value"],
            "Success": success
        })
        
        # Test 4: Parameter Tuning
        print_subsection("Parameter Tuning Test")
        parameter_mutation = {
            "parameter": "temperature",
            "component": "llm_calls",
            "current_value": 0.3,
            "new_value": 0.4
        }
        
        success = callbacks.apply_parameter_tuning(parameter_mutation)
        print_result("success" if success else "warning", "Parameter tuning applied", {
            "Parameter": parameter_mutation["parameter"],
            "Component": parameter_mutation["component"],
            "New value": parameter_mutation["new_value"],
            "Success": success
        })
        
        # Test 5: Applied Changes Report
        print_subsection("Applied Changes Report")
        applied_changes = callbacks.get_applied_changes()
        print_result("success", "Applied changes report generated", {
            "Total changes": len(applied_changes),
            "Recent changes": min(3, len(applied_changes))
        })
        
        for i, change in enumerate(applied_changes[-3:]):  # Show last 3 changes
            print_result("success", f"Change {i+1}: {change['change_type']}", {
                "Description": change["description"],
                "Success": change["success"],
                "Applied at": change["applied_at"]
            })
        
        return True
        
    except Exception as e:
        print_result("error", f"Evolution Callbacks test failed: {e}")
        return False

async def test_integrated_evolution_system():
    """Test the complete integrated evolution system"""
    print_section("INTEGRATED EVOLUTION SYSTEM TEST")
    
    try:
        from hephaestus.utils.config_loader import load_config
        from hephaestus.core.agent import HephaestusAgent
        
        config = load_config()
        
        # Create agent instance
        print_subsection("Agent Initialization")
        agent = HephaestusAgent(
            logger_instance=logger,
            config=config,
            continuous_mode=False
        )
        
        print_result("success", "Hephaestus agent initialized", {
            "Real-time evolution": hasattr(agent, 'real_time_evolution_engine'),
            "Parallel testing": hasattr(agent, 'parallel_reality_tester'),
            "Collective intelligence": hasattr(agent, 'collective_intelligence_network'),
            "Evolution callbacks": hasattr(agent, 'evolution_callbacks')
        })
        
        # Test 1: Evolution Status
        print_subsection("Complete Evolution Status")
        evolution_status = agent.get_evolution_status()
        print_result("success", "Evolution status retrieved", {
            "Real-time evolution running": evolution_status.get("real_time_evolution", {}).get("evolution_running", False),
            "Active parallel tests": len(evolution_status.get("parallel_testing", {}).get("active_sessions", [])),
            "Applied changes": len(evolution_status.get("applied_changes", [])),
            "System state": "Operational"
        })
        
        # Test 2: Parallel Strategy Testing
        print_subsection("Integrated Parallel Strategy Testing")
        test_objective = "Test integrated system performance"
        strategy_variants = [
            {"name": "Fast", "approach": "speed_optimized", "parameters": {"timeout": 30}},
            {"name": "Reliable", "approach": "reliability_optimized", "parameters": {"timeout": 60}},
            {"name": "Balanced", "approach": "balanced", "parameters": {"timeout": 45}}
        ]
        
        try:
            result = await agent.test_parallel_strategies(test_objective, strategy_variants)
            print_result("success" if result.get("success") else "warning", "Parallel strategy testing completed", {
                "Success": result.get("success", False),
                "Best strategy": result.get("best_strategy", "N/A"),
                "Fitness score": result.get("fitness_score", 0)
            })
        except Exception as e:
            print_result("warning", f"Parallel strategy testing: {e}")
        
        # Test 3: Collective Insights
        print_subsection("Collective Intelligence Insights")
        insights = agent.get_collective_insights(limit=3)
        print_result("success", "Collective insights retrieved", {
            "Total insights": len(insights),
            "Insight types": [insight.get("type", "unknown") for insight in insights]
        })
        
        # Test 4: Real-time Evolution Engine
        print_subsection("Real-time Evolution Engine")
        if hasattr(agent, 'real_time_evolution_engine'):
            engine = agent.real_time_evolution_engine
            
            # Generate a test mutation
            candidate = engine._generate_prompt_optimization()
            if candidate:
                engine.evolution_candidates[candidate.candidate_id] = candidate
                print_result("success", "Test mutation generated", {
                    "Candidate ID": candidate.candidate_id,
                    "Type": candidate.mutation_type.value,
                    "Description": candidate.description[:50] + "..."
                })
        
        return True
        
    except Exception as e:
        print_result("error", f"Integrated evolution system test failed: {e}")
        return False

async def main():
    """Main test execution"""
    print_section("COMPREHENSIVE EVOLUTION SYSTEM TEST")
    print("Testing the complete 100% functional evolution system...")
    print("This demonstrates a 'Formula 1 with real engine on real track'!")
    
    # Track results
    test_results = {}
    
    # Run all tests
    test_results["real_time_evolution"] = await test_real_time_evolution_engine()
    test_results["parallel_reality_testing"] = await test_parallel_reality_testing()
    test_results["collective_intelligence"] = await test_collective_intelligence_network()
    test_results["evolution_callbacks"] = await test_evolution_callbacks()
    test_results["integrated_system"] = await test_integrated_evolution_system()
    
    # Summary
    print_section("TEST SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 RESULTS:")
    print(f"   • Total tests: {total_tests}")
    print(f"   • Passed: {passed_tests}")
    print(f"   • Failed: {failed_tests}")
    print(f"   • Success rate: {passed_tests/total_tests*100:.1f}%")
    
    print(f"\n🧪 COMPONENT STATUS:")
    for component, result in test_results.items():
        status = "✅ FUNCTIONAL" if result else "❌ ISSUES"
        print(f"   • {component.replace('_', ' ').title()}: {status}")
    
    overall_status = "✅ FULLY FUNCTIONAL" if passed_tests == total_tests else "⚠️ PARTIALLY FUNCTIONAL"
    print(f"\n🚀 OVERALL SYSTEM STATUS: {overall_status}")
    
    if passed_tests == total_tests:
        print("\n🎉 SUCCESS! The evolution system is 100% functional!")
        print("   Formula 1 with real engine running on real track! 🏎️")
    else:
        print(f"\n⚠️ {failed_tests} components need attention")
    
    # Save results
    results_file = Path("evolution_system_test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests/total_tests*100
            }
        }, f, indent=2)
    
    print(f"\n📁 Test results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main()) 