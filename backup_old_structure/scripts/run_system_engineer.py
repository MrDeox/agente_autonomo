#!/usr/bin/env python3
"""
System Engineer Analysis Script

This script runs the System Engineer Agent to perform comprehensive analysis
of the Agente Autônomo codebase, identifying unused code, dead code, and
optimization opportunities.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.agents.system_engineer_agent import SystemEngineerAgent
from agent.config_loader import load_config


def setup_logging():
    """Setup logging for the analysis."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/system_engineer_analysis.log')
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main function to run system engineer analysis."""
    logger = setup_logging()
    
    logger.info("🔧 Starting System Engineer Analysis")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize System Engineer Agent
        system_engineer = SystemEngineerAgent(config, logger)
        logger.info("✅ System Engineer Agent initialized")
        
        # Run comprehensive analysis
        logger.info("🚀 Starting comprehensive codebase analysis...")
        report = system_engineer.run_analysis(project_root=".")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"reports/system_engineer_analysis_{timestamp}.json"
        
        os.makedirs("reports", exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")
        
        # Generate cleanup script
        cleanup_script = system_engineer.generate_cleanup_script(report)
        cleanup_file = f"scripts/cleanup_unused_code_{timestamp}.py"
        
        with open(cleanup_file, 'w', encoding='utf-8') as f:
            f.write(cleanup_script)
        
        logger.info(f"🔧 Cleanup script generated: {cleanup_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔧 SYSTEM ENGINEER ANALYSIS SUMMARY")
        print("=" * 60)
        
        summary = report['summary']
        findings = report['findings']
        
        print(f"📁 Files Analyzed: {summary['total_files_analyzed']}")
        print(f"🔧 Functions Found: {summary['total_functions']}")
        print(f"🏗️  Classes Found: {summary['total_classes']}")
        print(f"📦 Imports Found: {summary['total_imports']}")
        
        print("\n🔍 FINDINGS:")
        print(f"   • Unused Functions: {findings['unused_functions_count']}")
        print(f"   • Unused Classes: {findings['unused_classes_count']}")
        print(f"   • Dead Code Patterns: {findings['dead_code_count']}")
        print(f"   • Duplicate Code: {findings['duplicate_code_count']}")
        print(f"   • Performance Issues: {findings['performance_issues_count']}")
        print(f"   • Unused Dependencies: {findings['unused_dependencies_count']}")
        print(f"   • Optimization Opportunities: {findings['optimization_opportunities_count']}")
        
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"   {i}. {priority_emoji} {rec['action']}")
            print(f"      {rec['description']}")
            print(f"      Effort: {rec['estimated_effort']}")
            if 'files' in rec:
                print(f"      Files: {', '.join(rec['files'][:3])}{'...' if len(rec['files']) > 3 else ''}")
            print()
        
        # Show top unused functions
        if report['details']['unused_functions']:
            print("🗑️  TOP UNUSED FUNCTIONS:")
            for i, func in enumerate(report['details']['unused_functions'][:10], 1):
                print(f"   {i}. {func['name']} in {func['file']}:{func['line']}")
            if len(report['details']['unused_functions']) > 10:
                print(f"   ... and {len(report['details']['unused_functions']) - 10} more")
        
        # Show unused dependencies
        if report['details']['unused_dependencies']:
            print(f"\n📦 UNUSED DEPENDENCIES:")
            for dep in report['details']['unused_dependencies']:
                print(f"   • {dep}")
        
        print("\n" + "=" * 60)
        print("✅ Analysis completed successfully!")
        print(f"📄 Full report: {report_file}")
        print(f"🔧 Cleanup script: {cleanup_file}")
        print("=" * 60)
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main() 