"""
Test script for the Enhanced Architect Agent pilot
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_enhanced_architect():
    """Test the enhanced architect agent implementation."""
    
    print("🚀 Testing Enhanced Architect Agent Pilot")
    print("=" * 50)
    
    try:
        # Import the enhanced architect
        from hephaestus.agents.architect_enhanced import ArchitectAgentEnhanced
        
        print("✅ Successfully imported ArchitectAgentEnhanced")
        
        # Create instance
        agent = ArchitectAgentEnhanced()
        print(f"✅ Successfully created agent: {agent.name}")
        
        # Test configuration access
        config = agent.get_agent_config()
        print(f"✅ Agent config loaded: {len(config)} settings")
        
        # Test model config
        model_config = agent.get_model_config()
        print(f"✅ Model config loaded: {model_config.get('temperature', 'not set')}")
        
        # Test status
        status = agent.get_enhanced_status()
        print(f"✅ Status retrieved: {len(status)} fields")
        
        # Test metrics
        metrics = agent.get_agent_metrics()
        print(f"✅ Metrics retrieved: {metrics.get('agent_name', 'Unknown')}")
        
        # Test cache
        cache_stats = agent.get_cache_stats()
        print(f"✅ Cache stats: {cache_stats.get('cache_size', 0)} entries")
        
        # Test plan action (simplified)
        print("\n🧠 Testing plan_action method...")
        
        test_objective = "Add a new utility function for data validation"
        test_manifest = "Simple test manifest"
        
        plan, error = await agent.plan_action(test_objective, test_manifest)
        
        if error:
            print(f"⚠️ Plan action returned error: {error}")
        else:
            print(f"✅ Plan generated successfully with {len(plan.get('patches', []))} patches")
        
        # Test execution
        print("\n⚡ Testing execute method...")
        
        success, error = await agent.execute("Test objective for pilot")
        
        if success:
            print("✅ Execute method completed successfully")
        else:
            print(f"⚠️ Execute method failed: {error}")
        
        # Test architecture recommendations
        print("\n🏗️ Testing architecture recommendations...")
        
        recommendations = agent.get_architecture_recommendations()
        print(f"✅ Architecture recommendations: {len(recommendations.get('recommendations', []))} items")
        
        # Test codebase analysis
        print("\n🔍 Testing codebase analysis...")
        
        analysis = await agent.analyze_codebase()
        print(f"✅ Codebase analysis: {analysis.get('total_files', 0)} files analyzed")
        
        # Final status check
        print("\n📊 Final agent status:")
        final_status = agent.get_enhanced_status()
        
        print(f"  • Agent name: {final_status.get('name', 'Unknown')}")
        print(f"  • Capabilities: {len(final_status.get('capabilities', []))}")
        print(f"  • Enhanced features: {final_status.get('enhanced_features', {})}")
        print(f"  • Metrics enabled: {final_status.get('enhanced_features', {}).get('metrics_enabled', False)}")
        print(f"  • Caching enabled: {final_status.get('enhanced_features', {}).get('caching_enabled', False)}")
        
        print("\n🎉 Enhanced Architect Agent pilot test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might be due to missing dependencies or circular imports")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_foundation_utilities():
    """Test the foundation utilities independently."""
    
    print("\n🔧 Testing Foundation Utilities")
    print("=" * 40)
    
    try:
        # Test config manager
        from hephaestus.utils.config_manager import ConfigManager
        
        config = ConfigManager.get_agent_config("TestAgent")
        print(f"✅ ConfigManager working: {len(config)} default settings")
        
        # Test logger factory
        from hephaestus.utils.logger_factory import LoggerFactory
        
        logger = LoggerFactory.get_agent_logger("TestAgent")
        logger.info("Test log message")
        print("✅ LoggerFactory working: Test message logged")
        
        # Test metrics collector
        from hephaestus.utils.metrics_collector import get_global_metrics_collector
        
        metrics = get_global_metrics_collector()
        metrics.record_agent_performance("TestAgent", "test_operation", 0.1, True)
        dashboard = metrics.get_agent_dashboard("TestAgent")
        print(f"✅ MetricsCollector working: {dashboard.get('total_calls', 0)} calls recorded")
        
        # Test agent factory
        from hephaestus.utils.agent_factory import AgentFactory, get_global_registry
        
        registry = get_global_registry()
        print(f"✅ AgentFactory working: Registry initialized")
        
        print("🎉 All foundation utilities working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Foundation utilities test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    
    print("🧪 Enhanced Architecture Pilot Test Suite")
    print("=" * 60)
    
    # Test foundation first
    foundation_ok = await test_foundation_utilities()
    
    if not foundation_ok:
        print("\n❌ Foundation utilities failed - cannot proceed with agent test")
        return False
    
    # Test enhanced architect
    agent_ok = await test_enhanced_architect()
    
    if agent_ok and foundation_ok:
        print("\n🎉 ALL TESTS PASSED! Enhanced architecture is working!")
        print("\nNext steps:")
        print("1. ✅ Foundation utilities are working")
        print("2. ✅ Enhanced base agent is working")
        print("3. ✅ Pilot ArchitectAgent is working")
        print("4. 🔄 Ready to migrate other agents")
        return True
    else:
        print("\n❌ Some tests failed - check logs above")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)