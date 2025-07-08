"""
Feature Activator Agent - Integrates and Activates Unused Features

This agent takes the System Engineer analysis and activates all the unused
functions and features to make the system more comprehensive and functional.
"""

import os
import sys
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import json
import time
from datetime import datetime

from agent.utils.llm_client import call_llm_api


class FeatureActivatorAgent:
    """
    Feature Activator Agent that integrates unused functions and features.
    
    This agent:
    - Loads unused functions from System Engineer analysis
    - Integrates them into the main system workflow
    - Creates new capabilities using existing code
    - Activates dormant features
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.name = "feature_activator"
        
        # Load System Engineer analysis
        self.unused_functions = []
        self.unused_classes = []
        self.activated_features = []
        
        # Feature integration registry
        self.feature_registry = {}
        
        self.logger.info("🚀 Feature Activator Agent initialized")
    
    def load_analysis_results(self, analysis_file: str = None):
        """Load System Engineer analysis results."""
        if not analysis_file:
            # Find the most recent analysis file
            reports_dir = Path("reports")
            if reports_dir.exists():
                analysis_files = list(reports_dir.glob("system_engineer_analysis_*.json"))
                if analysis_files:
                    analysis_file = str(max(analysis_files, key=lambda x: x.stat().st_mtime))
        
        if analysis_file and os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            self.unused_functions = analysis['details']['unused_functions']
            self.unused_classes = analysis['details']['unused_classes']
            
            self.logger.info(f"📊 Loaded {len(self.unused_functions)} unused functions")
            self.logger.info(f"📊 Loaded {len(self.unused_classes)} unused classes")
        else:
            self.logger.warning("⚠️ No analysis file found, will scan manually")
    
    def categorize_unused_functions(self) -> Dict[str, List[Dict]]:
        """Categorize unused functions by their potential use."""
        categories = {
            'caching': [],
            'monitoring': [],
            'validation': [],
            'analysis': [],
            'optimization': [],
            'interface': [],
            'communication': [],
            'utilities': [],
            'testing': [],
            'other': []
        }
        
        for func in self.unused_functions:
            func_name = func['name'].lower()
            file_path = func['file'].lower()
            
            # Categorize based on function name and file path
            if any(keyword in func_name for keyword in ['cache', 'cached', 'cache_']):
                categories['caching'].append(func)
            elif any(keyword in func_name for keyword in ['monitor', 'watch', 'track', 'log']):
                categories['monitoring'].append(func)
            elif any(keyword in func_name for keyword in ['valid', 'check', 'verify', 'test']):
                categories['validation'].append(func)
            elif any(keyword in func_name for keyword in ['analyze', 'analysis', 'process']):
                categories['analysis'].append(func)
            elif any(keyword in func_name for keyword in ['optimize', 'improve', 'enhance']):
                categories['optimization'].append(func)
            elif any(keyword in func_name for keyword in ['interface', 'ui', 'gui', 'display']):
                categories['interface'].append(func)
            elif any(keyword in func_name for keyword in ['comm', 'message', 'send', 'receive']):
                categories['communication'].append(func)
            elif 'test' in file_path:
                categories['testing'].append(func)
            elif any(keyword in func_name for keyword in ['util', 'helper', 'format', 'parse']):
                categories['utilities'].append(func)
            else:
                categories['other'].append(func)
        
        return categories
    
    def activate_caching_features(self):
        """Activate unused caching functions."""
        self.logger.info("💾 Activating caching features...")
        
        # Find caching functions
        cache_functions = [
            func for func in self.unused_functions 
            if any(keyword in func['name'].lower() for keyword in ['cache', 'cached'])
        ]
        
        for func in cache_functions:
            try:
                # Import and activate the function
                module_path = func['file'].replace('./', '').replace('.py', '').replace('/', '.')
                module = importlib.import_module(module_path)
                
                if hasattr(module, func['name']):
                    function = getattr(module, func['name'])
                    
                    # Register the function for use
                    self.feature_registry[f"cache_{func['name']}"] = {
                        'function': function,
                        'module': module,
                        'type': 'caching',
                        'description': f"Caching function from {func['file']}"
                    }
                    
                    self.activated_features.append({
                        'name': func['name'],
                        'type': 'caching',
                        'file': func['file'],
                        'status': 'activated'
                    })
                    
                    self.logger.info(f"✅ Activated caching function: {func['name']}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not activate {func['name']}: {e}")
    
    def activate_monitoring_features(self):
        """Activate unused monitoring functions."""
        self.logger.info("📊 Activating monitoring features...")
        
        # Find monitoring functions
        monitor_functions = [
            func for func in self.unused_functions 
            if any(keyword in func['name'].lower() for keyword in ['monitor', 'watch', 'track', 'log'])
        ]
        
        for func in monitor_functions:
            try:
                # Import and activate the function
                module_path = func['file'].replace('./', '').replace('.py', '').replace('/', '.')
                module = importlib.import_module(module_path)
                
                if hasattr(module, func['name']):
                    function = getattr(module, func['name'])
                    
                    # Register the function for use
                    self.feature_registry[f"monitor_{func['name']}"] = {
                        'function': function,
                        'module': module,
                        'type': 'monitoring',
                        'description': f"Monitoring function from {func['file']}"
                    }
                    
                    self.activated_features.append({
                        'name': func['name'],
                        'type': 'monitoring',
                        'file': func['file'],
                        'status': 'activated'
                    })
                    
                    self.logger.info(f"✅ Activated monitoring function: {func['name']}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not activate {func['name']}: {e}")
    
    def activate_validation_features(self):
        """Activate unused validation functions."""
        self.logger.info("✅ Activating validation features...")
        
        # Find validation functions
        validation_functions = [
            func for func in self.unused_functions 
            if any(keyword in func['name'].lower() for keyword in ['valid', 'check', 'verify', 'test'])
        ]
        
        for func in validation_functions:
            try:
                # Import and activate the function
                module_path = func['file'].replace('./', '').replace('.py', '').replace('/', '.')
                module = importlib.import_module(module_path)
                
                if hasattr(module, func['name']):
                    function = getattr(module, func['name'])
                    
                    # Register the function for use
                    self.feature_registry[f"validate_{func['name']}"] = {
                        'function': function,
                        'module': module,
                        'type': 'validation',
                        'description': f"Validation function from {func['file']}"
                    }
                    
                    self.activated_features.append({
                        'name': func['name'],
                        'type': 'validation',
                        'file': func['file'],
                        'status': 'activated'
                    })
                    
                    self.logger.info(f"✅ Activated validation function: {func['name']}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not activate {func['name']}: {e}")
    
    def activate_interface_features(self):
        """Activate unused interface functions."""
        self.logger.info("🖥️ Activating interface features...")
        
        # Find interface functions
        interface_functions = [
            func for func in self.unused_functions 
            if any(keyword in func['name'].lower() for keyword in ['interface', 'ui', 'gui', 'display', 'generate'])
        ]
        
        for func in interface_functions:
            try:
                # Import and activate the function
                module_path = func['file'].replace('./', '').replace('.py', '').replace('/', '.')
                module = importlib.import_module(module_path)
                
                if hasattr(module, func['name']):
                    function = getattr(module, func['name'])
                    
                    # Register the function for use
                    self.feature_registry[f"interface_{func['name']}"] = {
                        'function': function,
                        'module': module,
                        'type': 'interface',
                        'description': f"Interface function from {func['file']}"
                    }
                    
                    self.activated_features.append({
                        'name': func['name'],
                        'type': 'interface',
                        'file': func['file'],
                        'status': 'activated'
                    })
                    
                    self.logger.info(f"✅ Activated interface function: {func['name']}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not activate {func['name']}: {e}")
    
    def create_integrated_workflows(self):
        """Create integrated workflows using activated features."""
        self.logger.info("🔄 Creating integrated workflows...")
        
        workflows = {
            'enhanced_monitoring': {
                'description': 'Enhanced system monitoring using all monitoring features',
                'steps': []
            },
            'smart_caching': {
                'description': 'Intelligent caching system using all caching features',
                'steps': []
            },
            'comprehensive_validation': {
                'description': 'Multi-layer validation using all validation features',
                'steps': []
            },
            'dynamic_interface': {
                'description': 'Dynamic interface generation using all interface features',
                'steps': []
            }
        }
        
        # Build workflows based on activated features
        for feature_name, feature_info in self.feature_registry.items():
            if feature_info['type'] == 'monitoring':
                workflows['enhanced_monitoring']['steps'].append(feature_name)
            elif feature_info['type'] == 'caching':
                workflows['smart_caching']['steps'].append(feature_name)
            elif feature_info['type'] == 'validation':
                workflows['comprehensive_validation']['steps'].append(feature_name)
            elif feature_info['type'] == 'interface':
                workflows['dynamic_interface']['steps'].append(feature_name)
        
        return workflows
    
    def integrate_with_main_system(self):
        """Integrate activated features with the main system."""
        self.logger.info("🔗 Integrating features with main system...")
        
        # Try to integrate with tools/app.py
        try:
            import tools.app as main_app
            
            # Add activated features to the main app
            for feature_name, feature_info in self.feature_registry.items():
                if hasattr(main_app, 'app'):
                    # Add feature to FastAPI app
                    setattr(main_app, f"activated_{feature_name}", feature_info['function'])
                    
                    # Create endpoint for the feature
                    if feature_info['type'] == 'monitoring':
                        # Add monitoring endpoint
                        pass
                    elif feature_info['type'] == 'caching':
                        # Add caching endpoint
                        pass
                    elif feature_info['type'] == 'validation':
                        # Add validation endpoint
                        pass
                    elif feature_info['type'] == 'interface':
                        # Add interface endpoint
                        pass
            
            self.logger.info("✅ Features integrated with main system")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not integrate with main system: {e}")
    
    def run_activation(self) -> Dict[str, Any]:
        """Run the complete feature activation process."""
        self.logger.info("🚀 Starting Feature Activation Process")
        self.logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Load analysis results
            self.load_analysis_results()
            
            # Categorize functions
            categories = self.categorize_unused_functions()
            
            # Activate features by category
            self.activate_caching_features()
            self.activate_monitoring_features()
            self.activate_validation_features()
            self.activate_interface_features()
            
            # Create integrated workflows
            workflows = self.create_integrated_workflows()
            
            # Integrate with main system
            self.integrate_with_main_system()
            
            activation_time = time.time() - start_time
            
            # Generate report
            report = {
                'summary': {
                    'total_functions_analyzed': len(self.unused_functions),
                    'total_classes_analyzed': len(self.unused_classes),
                    'features_activated': len(self.activated_features),
                    'workflows_created': len(workflows),
                    'activation_time': activation_time
                },
                'categories': categories,
                'activated_features': self.activated_features,
                'feature_registry': {k: {'type': v['type'], 'description': v['description']} 
                                   for k, v in self.feature_registry.items()},
                'workflows': workflows,
                'recommendations': self._generate_activation_recommendations()
            }
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"reports/feature_activation_{timestamp}.json"
            
            os.makedirs("reports", exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📄 Activation report saved to: {report_file}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error during feature activation: {e}")
            raise
    
    def _generate_activation_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for using activated features."""
        recommendations = []
        
        if self.feature_registry:
            recommendations.append({
                'priority': 'high',
                'action': 'Use activated caching features',
                'description': f"Activated {len([f for f in self.feature_registry.values() if f['type'] == 'caching'])} caching functions",
                'benefit': 'Improved performance and reduced API calls'
            })
            
            recommendations.append({
                'priority': 'high',
                'action': 'Use activated monitoring features',
                'description': f"Activated {len([f for f in self.feature_registry.values() if f['type'] == 'monitoring'])} monitoring functions",
                'benefit': 'Better system observability and debugging'
            })
            
            recommendations.append({
                'priority': 'medium',
                'action': 'Use activated validation features',
                'description': f"Activated {len([f for f in self.feature_registry.values() if f['type'] == 'validation'])} validation functions",
                'benefit': 'Enhanced data validation and error prevention'
            })
            
            recommendations.append({
                'priority': 'medium',
                'action': 'Use activated interface features',
                'description': f"Activated {len([f for f in self.feature_registry.values() if f['type'] == 'interface'])} interface functions",
                'benefit': 'Better user experience and interface generation'
            })
        
        return recommendations 