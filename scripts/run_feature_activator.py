#!/usr/bin/env python3
"""
Feature Activator Script

This script runs the Feature Activator Agent to integrate and activate
all unused functions and features identified by the System Engineer analysis.
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

from agent.feature_activator_agent import FeatureActivatorAgent
from agent.config_loader import load_config


def setup_logging():
    """Setup logging for the feature activation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/feature_activation.log')
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main function to run feature activation."""
    logger = setup_logging()
    
    logger.info("🚀 Starting Feature Activation Process")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize Feature Activator Agent
        feature_activator = FeatureActivatorAgent(config, logger)
        logger.info("✅ Feature Activator Agent initialized")
        
        # Run feature activation
        logger.info("🚀 Starting feature activation...")
        report = feature_activator.run_activation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🚀 FEATURE ACTIVATION SUMMARY")
        print("=" * 60)
        
        summary = report['summary']
        print(f"📊 Functions Analyzed: {summary['total_functions_analyzed']}")
        print(f"📊 Classes Analyzed: {summary['total_classes_analyzed']}")
        print(f"✅ Features Activated: {summary['features_activated']}")
        print(f"🔄 Workflows Created: {summary['workflows_created']}")
        print(f"⏱️  Activation Time: {summary['activation_time']:.2f}s")
        
        print("\n📋 ACTIVATED FEATURES BY CATEGORY:")
        categories = report['categories']
        for category, functions in categories.items():
            if functions:
                print(f"   • {category.title()}: {len(functions)} functions")
        
        print("\n✅ ACTIVATED FEATURES:")
        for feature in report['activated_features'][:10]:  # Show first 10
            print(f"   • {feature['name']} ({feature['type']}) - {feature['file']}")
        
        if len(report['activated_features']) > 10:
            print(f"   ... and {len(report['activated_features']) - 10} more")
        
        print("\n🔄 CREATED WORKFLOWS:")
        for workflow_name, workflow_info in report['workflows'].items():
            print(f"   • {workflow_name}: {workflow_info['description']}")
            print(f"     Steps: {len(workflow_info['steps'])}")
        
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"   {i}. {priority_emoji} {rec['action']}")
            print(f"      {rec['description']}")
            print(f"      Benefit: {rec['benefit']}")
            print()
        
        print("=" * 60)
        print("✅ Feature activation completed successfully!")
        print("🚀 The system now uses more of its developed capabilities!")
        print("=" * 60)
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Error during feature activation: {e}")
        raise


if __name__ == "__main__":
    main() 