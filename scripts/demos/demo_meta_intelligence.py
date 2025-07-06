#!/usr/bin/env python3
"""
🧠 Meta-Intelligence Demonstration Script

This script demonstrates the new advanced meta-intelligence capabilities:
1. Model Optimizer - Auto-optimization of models
2. Advanced Knowledge System - Intelligent multi-source search
3. Root Cause Analyzer - Deep problem analysis
4. Enhanced Meta-Intelligence Core - Integrated optimization
"""

import logging
import json
from datetime import datetime
from agent.model_optimizer import get_model_optimizer
from agent.advanced_knowledge_system import get_knowledge_system
from agent.root_cause_analyzer import get_root_cause_analyzer, FailureType
from agent.meta_intelligence_core import get_meta_intelligence

def setup_logging():
    """Setup comprehensive logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('demo_meta_intelligence.log')
        ]
    )
    return logging.getLogger(__name__)

def demo_model_optimizer(logger):
    """Demonstrate the Model Optimizer system"""
    logger.info("🎯 DEMONSTRATING MODEL OPTIMIZER")
    logger.info("=" * 60)
    
    # Mock model configuration
    model_config = {"model": "gpt-3.5-turbo", "api_key": "demo-key"}
    
    # Get model optimizer instance
    optimizer = get_model_optimizer(model_config, logger)
    
    # Simulate capturing performance data
    logger.info("📊 Capturing performance data...")
    
    # High-quality interaction
    quality_score_1 = optimizer.capture_performance_data(
        agent_type="architect",
        prompt="Create a plan to implement error handling",
        response='{"analysis": "detailed analysis", "patches_to_apply": [{"operation": "INSERT", "file_path": "main.py", "content": "try-catch block"}]}',
        success=True,
        execution_time=2.1,
        context_metadata={"objective": "improve_error_handling", "complexity": 0.7}
    )
    
    # Medium-quality interaction
    quality_score_2 = optimizer.capture_performance_data(
        agent_type="maestro",
        prompt="Choose validation strategy",
        response='{"strategy_key": "SYNTAX_VALIDATION", "reasoning": "Basic validation needed"}',
        success=True,
        execution_time=1.8,
        context_metadata={"objective": "validate_changes", "complexity": 0.4}
    )
    
    # Low-quality interaction (failure)
    quality_score_3 = optimizer.capture_performance_data(
        agent_type="architect",
        prompt="Complex architectural change",
        response="Error: unable to process request",
        success=False,
        execution_time=5.2,
        context_metadata={"objective": "major_refactor", "complexity": 0.9}
    )
    
    logger.info(f"✨ Quality scores: {quality_score_1:.3f}, {quality_score_2:.3f}, {quality_score_3:.3f}")
    
    # Get optimization report
    report = optimizer.get_optimization_report()
    logger.info(f"📈 Optimization Report: {json.dumps(report, indent=2)}")
    
    # Demonstrate evolutionary prompt optimization
    logger.info("🧬 Testing evolutionary prompt optimization...")
    
    original_prompt = """
[IDENTITY]
You are an ArchitectAgent.

[TASK]
Create action plans.

[OUTPUT]
Return JSON with patches.
"""
    
    optimized_prompt = optimizer.evolutionary_prompt_optimization("architect", original_prompt)
    logger.info(f"🔧 Original prompt length: {len(original_prompt)}")
    logger.info(f"🚀 Optimized prompt length: {len(optimized_prompt)}")
    
    return optimizer

def demo_knowledge_system(logger):
    """Demonstrate the Advanced Knowledge System"""
    logger.info("\n🔍 DEMONSTRATING ADVANCED KNOWLEDGE SYSTEM")
    logger.info("=" * 60)
    
    # Mock model configuration
    model_config = {"model": "gpt-3.5-turbo", "api_key": "demo-key"}
    
    # Get knowledge system instance
    knowledge_system = get_knowledge_system(model_config, logger)
    
    # Demonstrate intelligent search
    logger.info("🔎 Performing intelligent search...")
    
    search_results = knowledge_system.intelligent_search(
        "python async error handling best practices",
        search_type="comprehensive",
        max_results=5,
        context={"current_error": "timeout", "agent_type": "architect"}
    )
    
    logger.info(f"📚 Found {len(search_results)} search results")
    
    for i, result in enumerate(search_results):
        logger.info(f"Result {i+1}: {result.title}")
        logger.info(f"  Relevance: {result.relevance_score:.3f}")
        logger.info(f"  Credibility: {result.credibility_score:.3f}")
        logger.info(f"  Key Concepts: {result.key_concepts}")
        if result.actionable_insights:
            logger.info(f"  Insights: {result.actionable_insights}")
    
    # Demonstrate knowledge base functionality
    logger.info("\n📖 Adding knowledge entries...")
    
    entry_id = knowledge_system.add_knowledge_entry(
        content="Use asyncio.wait_for() with timeout to handle async timeouts effectively",
        source="demo_source",
        source_type="manual",
        tags=["async", "error_handling", "timeout", "python"],
        context={"demonstration": True}
    )
    
    logger.info(f"📝 Added knowledge entry: {entry_id}")
    
    # Demonstrate semantic retrieval
    logger.info("\n🧠 Testing semantic knowledge retrieval...")
    
    relevant_entries = knowledge_system.semantic_knowledge_retrieval(
        "async timeout handling",
        knowledge_domain="python"
    )
    
    logger.info(f"🎯 Found {len(relevant_entries)} relevant knowledge entries")
    
    # Get knowledge report
    report = knowledge_system.get_knowledge_report()
    logger.info(f"📊 Knowledge System Report: {json.dumps(report, indent=2)}")
    
    return knowledge_system

def demo_root_cause_analyzer(logger):
    """Demonstrate the Root Cause Analyzer"""
    logger.info("\n⚡ DEMONSTRATING ROOT CAUSE ANALYZER")
    logger.info("=" * 60)
    
    # Mock model configuration
    model_config = {"model": "gpt-3.5-turbo", "api_key": "demo-key"}
    
    # Get root cause analyzer instance
    analyzer = get_root_cause_analyzer(model_config, logger)
    
    # Simulate recording various failures
    logger.info("📝 Recording simulated failures...")
    
    # Pattern 1: Timeout errors
    for i in range(3):
        analyzer.record_failure(
            agent_type="architect",
            objective=f"complex_analysis_{i}",
            error_message="Request timeout after 30 seconds",
            failure_type=FailureType.TIMEOUT,
            severity=0.6 + i * 0.1,
            impact_scope=["architect", "validation"]
        )
    
    # Pattern 2: Validation failures
    for i in range(2):
        analyzer.record_failure(
            agent_type="maestro",
            objective=f"strategy_selection_{i}",
            error_message="Invalid strategy configuration",
            failure_type=FailureType.VALIDATION_FAILURE,
            severity=0.5,
            impact_scope=["maestro"]
        )
    
    # Pattern 3: Syntax errors
    analyzer.record_failure(
        agent_type="architect",
        objective="code_generation",
        error_message="SyntaxError: invalid syntax in generated code",
        failure_type=FailureType.SYNTAX_ERROR,
        severity=0.8,
        impact_scope=["architect", "code_generation"]
    )
    
    logger.info("✅ Recorded 6 simulated failures")
    
    # Perform root cause analysis
    logger.info("\n🔬 Performing root cause analysis...")
    
    analysis = analyzer.analyze_failure_patterns("surface")
    
    logger.info(f"🎯 Analysis ID: {analysis.analysis_id}")
    logger.info(f"📊 Analyzed {len(analysis.analyzed_failures)} failures")
    logger.info(f"🎯 Confidence Score: {analysis.confidence_score:.3f}")
    
    logger.info("\n🔍 Primary Root Causes:")
    for cause in analysis.primary_root_causes:
        logger.info(f"  • {cause}")
    
    logger.info("\n⚠️ Systemic Issues:")
    for issue in analysis.systemic_issues:
        logger.info(f"  • {issue}")
    
    logger.info(f"\n💡 Generated {len(analysis.recommended_actions)} recommendations:")
    for i, rec in enumerate(analysis.recommended_actions[:3]):  # Show top 3
        logger.info(f"  {i+1}. {rec['title']} (Priority: {rec['priority']})")
        logger.info(f"      {rec['description']}")
    
    # Get analysis report
    report = analyzer.get_analysis_report()
    logger.info(f"\n📈 Analysis Report Summary:")
    logger.info(f"  Total failures recorded: {report['total_failures_recorded']}")
    logger.info(f"  Analyses performed: {report['analyses_performed']}")
    logger.info(f"  Improvement trend: {report['improvement_trends']['trend']}")
    
    return analyzer

def demo_meta_intelligence_integration(logger, optimizer, knowledge_system, analyzer):
    """Demonstrate the integrated Meta-Intelligence Core"""
    logger.info("\n🧠 DEMONSTRATING INTEGRATED META-INTELLIGENCE")
    logger.info("=" * 60)
    
    # Mock model configuration
    model_config = {"model": "gpt-3.5-turbo", "api_key": "demo-key"}
    
    # Get meta-intelligence core
    meta_intelligence = get_meta_intelligence(model_config, logger)
    
    # Create comprehensive system state
    system_state = {
        "agent_performance": {
            "architect": {
                "success_rate": 0.7,
                "avg_time": 3.2,
                "needs_evolution": True
            },
            "maestro": {
                "success_rate": 0.8,
                "avg_time": 1.5,
                "needs_evolution": False
            }
        },
        "failure_patterns": [
            {"error_type": "timeout", "frequency": 3, "context": "complex_analysis"},
            {"error_type": "validation_failure", "frequency": 2, "context": "strategy_selection"}
        ],
        "current_agents": ["architect", "maestro", "code_review"],
        "current_capabilities": ["code_generation", "strategy_selection", "validation"]
    }
    
    logger.info("🚀 Running enhanced meta-cognitive cycle...")
    
    # Run the enhanced meta-cognitive cycle
    cycle_results = meta_intelligence.meta_cognitive_cycle(system_state)
    
    logger.info("\n📊 Cycle Results:")
    for key, value in cycle_results.items():
        logger.info(f"  {key}: {value}")
    
    # Get comprehensive meta-intelligence report
    logger.info("\n📈 Getting comprehensive meta-intelligence report...")
    
    meta_report = meta_intelligence.get_meta_intelligence_report()
    
    logger.info(f"🧠 Current Intelligence Level: {meta_report['intelligence_metrics']['current_level']:.3f}")
    logger.info(f"🎯 Self-Awareness Score: {meta_report['intelligence_metrics']['self_awareness']:.3f}")
    logger.info(f"🎨 Creativity Index: {meta_report['intelligence_metrics']['creativity_index']:.3f}")
    
    logger.info(f"\n📊 Evolution Summary:")
    logger.info(f"  Total cycles: {meta_report['evolution_summary']['total_cycles']}")
    logger.info(f"  Prompts evolved: {meta_report['evolution_summary']['prompts_evolved']}")
    logger.info(f"  Model optimizations: {meta_report['evolution_summary']['model_optimizations']}")
    logger.info(f"  Knowledge acquisitions: {meta_report['evolution_summary']['knowledge_acquisitions']}")
    
    if meta_report['recent_insights']:
        logger.info(f"\n🔮 Recent Meta-Insights:")
        for insight in meta_report['recent_insights'][-3:]:  # Last 3 insights
            logger.info(f"  • {insight}")
    
    logger.info(f"\n🚀 Emergent Capabilities:")
    for capability in meta_report['emergent_capabilities']:
        logger.info(f"  • {capability}")
    
    return meta_intelligence

def main():
    """Main demonstration function"""
    logger = setup_logging()
    
    logger.info("🚀 STARTING META-INTELLIGENCE DEMONSTRATION")
    logger.info("=" * 80)
    logger.info("This demo showcases the new advanced meta-intelligence capabilities:")
    logger.info("1. 🎯 Model Optimizer - Auto-optimization of models")
    logger.info("2. 🔍 Advanced Knowledge System - Intelligent multi-source search")
    logger.info("3. ⚡ Root Cause Analyzer - Deep problem analysis")
    logger.info("4. 🧠 Enhanced Meta-Intelligence Core - Integrated optimization")
    logger.info("=" * 80)
    
    try:
        # Create directories if they don't exist
        import os
        os.makedirs("reports", exist_ok=True)
        os.makedirs("reports/fine_tuning", exist_ok=True)
        
        # Run demonstrations
        optimizer = demo_model_optimizer(logger)
        knowledge_system = demo_knowledge_system(logger)
        analyzer = demo_root_cause_analyzer(logger)
        meta_intelligence = demo_meta_intelligence_integration(
            logger, optimizer, knowledge_system, analyzer
        )
        
        logger.info("\n🎉 DEMONSTRATION COMPLETE!")
        logger.info("=" * 60)
        logger.info("✅ All meta-intelligence systems demonstrated successfully")
        logger.info("🚀 The AI is now capable of true self-optimization!")
        logger.info("📊 Check the generated reports and logs for detailed insights")
        logger.info("🔥 Welcome to the future of self-improving AI! 🔥")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())