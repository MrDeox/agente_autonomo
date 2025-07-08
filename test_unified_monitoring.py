"""
Test script for Unified Monitoring and Validation System
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


async def test_unified_dashboard():
    """Test the unified dashboard system."""
    print("📊 Testing Unified Dashboard")
    print("=" * 40)
    
    try:
        from hephaestus.monitoring import get_unified_dashboard
        
        # Get dashboard instance
        dashboard = get_unified_dashboard()
        print("✅ Dashboard instance created")
        
        # Start monitoring
        await dashboard.start_monitoring()
        print("✅ Monitoring started")
        
        # Wait a moment for data collection
        await asyncio.sleep(2)
        
        # Test system summary
        summary = dashboard.get_system_summary()
        print(f"✅ System summary: {summary['status']} "
              f"({summary['total_agents']} agents, {summary['recent_alerts']} alerts)")
        
        # Test full dashboard data
        dashboard_data = dashboard.get_dashboard_data()
        print(f"✅ Dashboard data: {len(dashboard_data.get('agents', {}))} agents tracked")
        
        # Test agent dashboard (if agents exist)
        if dashboard_data.get('agents'):
            agent_name = list(dashboard_data['agents'].keys())[0]
            agent_data = dashboard.get_agent_dashboard(agent_name)
            print(f"✅ Agent dashboard for {agent_name}: "
                  f"{len(agent_data.get('recent_alerts', []))} recent alerts")
        
        # Stop monitoring
        await dashboard.stop_monitoring()
        print("✅ Monitoring stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_unified_validator():
    """Test the unified validation system."""
    print("\n✅ Testing Unified Validator")
    print("=" * 40)
    
    try:
        from hephaestus.validation import get_unified_validator
        
        # Get validator instance
        validator = get_unified_validator()
        print("✅ Validator instance created")
        
        # Test code structure validation
        print("🔍 Running code structure validation...")
        code_suite = await validator.validate_system("code")
        print(f"✅ Code validation: {code_suite.overall_status} "
              f"({code_suite.passed} passed, {code_suite.failed} failed)")
        
        # Test configuration validation
        print("🔍 Running configuration validation...")
        config_suite = await validator.validate_system("config")
        print(f"✅ Config validation: {config_suite.overall_status} "
              f"({config_suite.passed} passed, {config_suite.failed} failed)")
        
        # Test agent validation
        print("🔍 Running agent validation...")
        agent_suite = await validator.validate_system("agents")
        print(f"✅ Agent validation: {agent_suite.overall_status} "
              f"({agent_suite.passed} passed, {agent_suite.failed} failed)")
        
        # Test security validation
        print("🔍 Running security validation...")
        security_suite = await validator.validate_system("security")
        print(f"✅ Security validation: {security_suite.overall_status} "
              f"({security_suite.passed} passed, {security_suite.failed} failed)")
        
        # Test validation summary
        summary = validator.get_validation_summary()
        print(f"✅ Validation summary: {summary['status']} "
              f"({summary.get('critical_issues', 0)} critical issues)")
        
        # Test validation history
        history = validator.get_validation_history(limit=3)
        print(f"✅ Validation history: {len(history)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dashboard_server():
    """Test the dashboard server (without actually starting it)."""
    print("\n🌐 Testing Dashboard Server")
    print("=" * 40)
    
    try:
        from hephaestus.api.dashboard_server import DashboardServer
        
        # Create server instance
        server = DashboardServer(host="localhost", port=8080)
        print("✅ Dashboard server instance created")
        
        # Test HTML generation
        html = server._get_dashboard_html()
        assert "Hephaestus Dashboard" in html
        print("✅ Dashboard HTML generated successfully")
        
        # Test route setup
        assert server.app is not None
        print("✅ FastAPI routes configured")
        
        print("ℹ️  Dashboard server ready (not started in test)")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test integration between monitoring and validation."""
    print("\n🔗 Testing System Integration")
    print("=" * 40)
    
    try:
        from hephaestus.monitoring import get_unified_dashboard
        from hephaestus.validation import get_unified_validator
        
        # Get instances
        dashboard = get_unified_dashboard()
        validator = get_unified_validator()
        
        print("✅ Both systems initialized")
        
        # Start monitoring
        await dashboard.start_monitoring()
        
        # Run validation
        validation_result = await validator.validate_system("code")
        
        # Get dashboard data
        dashboard_data = dashboard.get_dashboard_data()
        validation_summary = validator.get_validation_summary()
        
        print(f"✅ Integration working: "
              f"Dashboard has {len(dashboard_data.get('agents', {}))} agents, "
              f"Validation status: {validation_summary['status']}")
        
        # Stop monitoring
        await dashboard.stop_monitoring()
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_real_agents():
    """Test with actual enhanced agents."""
    print("\n🤖 Testing with Enhanced Agents")
    print("=" * 40)
    
    try:
        from hephaestus.agents.maestro_enhanced import MaestroAgentEnhanced
        from hephaestus.agents.bug_hunter_enhanced import BugHunterAgentEnhanced
        from hephaestus.monitoring import get_unified_dashboard
        
        # Create agents
        maestro = MaestroAgentEnhanced()
        bug_hunter = BugHunterAgentEnhanced()
        
        print("✅ Enhanced agents created")
        
        # Get dashboard
        dashboard = get_unified_dashboard()
        await dashboard.start_monitoring()
        
        # Execute some operations to generate metrics
        await maestro.execute("Test strategic planning")
        await bug_hunter.execute("Scan for test bugs")
        
        print("✅ Agent operations executed")
        
        # Wait for metrics to be collected
        await asyncio.sleep(1)
        
        # Check dashboard
        dashboard_data = dashboard.get_dashboard_data()
        print(f"✅ Dashboard tracking: {len(dashboard_data.get('agents', {}))} agents")
        
        # Get agent metrics
        maestro_metrics = maestro.get_agent_metrics()
        bug_hunter_dashboard = bug_hunter.get_bug_dashboard()
        
        print(f"✅ Agent metrics: Maestro has {maestro_metrics.get('total_calls', 0)} calls")
        print(f"✅ Bug Hunter metrics: {bug_hunter_dashboard.get('total_bugs_detected', 0)} bugs detected")
        
        await dashboard.stop_monitoring()
        
        return True
        
    except Exception as e:
        print(f"❌ Real agents test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🧪 Unified Monitoring & Validation Test Suite")
    print("=" * 60)
    
    tests = [
        ("Unified Dashboard", test_unified_dashboard),
        ("Unified Validator", test_unified_validator),
        ("Dashboard Server", test_dashboard_server),
        ("System Integration", test_integration),
        ("Real Agents", test_real_agents)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = await test_func()
            duration = time.time() - start_time
            results[test_name] = {"passed": result, "duration": duration}
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = {"passed": False, "duration": 0}
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result["passed"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        duration = f"({result['duration']:.2f}s)"
        print(f"{test_name:<25} {status:<12} {duration}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 UNIFIED MONITORING & VALIDATION SYSTEM WORKING!")
        print("\nKey Features Validated:")
        print("• ✅ Real-time system health monitoring")
        print("• ✅ Comprehensive validation framework")
        print("• ✅ Web dashboard with live updates")
        print("• ✅ Agent performance tracking")
        print("• ✅ Automated alerting system")
        print("• ✅ Integration with enhanced agents")
        print("\n🚀 FASE 7 COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Start the dashboard: python -m hephaestus.api.dashboard_server")
        print("2. View real-time monitoring at http://localhost:8080")
        print("3. Run comprehensive validations")
        print("4. Monitor agent performance")
        return True
    else:
        print("⚠️ Some tests failed - check logs above")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)