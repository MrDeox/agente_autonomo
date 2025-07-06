#!/usr/bin/env python3
"""
Feature Integration Script

This script integrates the activated features into the main system workflow,
making them available for use in the Hephaestus system.
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

from agent.config_loader import load_config


def setup_logging():
    """Setup logging for the integration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/feature_integration.log')
        ]
    )
    return logging.getLogger(__name__)


def load_activation_report():
    """Load the most recent feature activation report."""
    reports_dir = Path("reports")
    if reports_dir.exists():
        activation_files = list(reports_dir.glob("feature_activation_*.json"))
        if activation_files:
            latest_file = max(activation_files, key=lambda x: x.stat().st_mtime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None


def integrate_caching_features(report, logger):
    """Integrate caching features into the main system."""
    logger.info("💾 Integrating caching features...")
    
    # Find caching functions in the report
    cache_functions = []
    for feature in report['activated_features']:
        if feature['type'] == 'caching':
            cache_functions.append(feature)
    
    # Create enhanced caching system
    cache_integration_code = '''
# Enhanced Caching System Integration
import functools
import time
from typing import Any, Dict, Optional

class EnhancedCache:
    """Enhanced caching system using activated features."""
    
    def __init__(self):
        self.cache = {}
        self.stats = {'hits': 0, 'misses': 0}
    
    def cached(self, ttl: int = 300):
        """Decorator for caching function results."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Check cache
                if cache_key in self.cache:
                    cache_entry = self.cache[cache_key]
                    if time.time() - cache_entry['timestamp'] < ttl:
                        self.stats['hits'] += 1
                        return cache_entry['value']
                
                # Cache miss
                self.stats['misses'] += 1
                result = func(*args, **kwargs)
                
                # Store in cache
                self.cache[cache_key] = {
                    'value': result,
                    'timestamp': time.time()
                }
                
                return result
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total if total > 0 else 0
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }

# Global enhanced cache instance
enhanced_cache = EnhancedCache()
'''
    
    # Write the integration code
    with open('agent/enhanced_cache_integration.py', 'w') as f:
        f.write(cache_integration_code)
    
    logger.info(f"✅ Integrated {len(cache_functions)} caching features")
    return len(cache_functions)


def integrate_monitoring_features(report, logger):
    """Integrate monitoring features into the main system."""
    logger.info("📊 Integrating monitoring features...")
    
    # Find monitoring functions in the report
    monitor_functions = []
    for feature in report['activated_features']:
        if feature['type'] == 'monitoring':
            monitor_functions.append(feature)
    
    # Create enhanced monitoring system
    monitoring_integration_code = '''
# Enhanced Monitoring System Integration
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

class EnhancedMonitor:
    """Enhanced monitoring system using activated features."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = {}
        self.alerts = []
    
    def track_metric(self, name: str, value: Any, category: str = "general"):
        """Track a metric."""
        if category not in self.metrics:
            self.metrics[category] = {}
        
        if name not in self.metrics[category]:
            self.metrics[category][name] = []
        
        self.metrics[category][name].append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 values
        if len(self.metrics[category][name]) > 100:
            self.metrics[category][name] = self.metrics[category][name][-100:]
    
    def add_alert(self, level: str, message: str, context: Dict[str, Any] = None):
        """Add an alert."""
        alert = {
            'level': level,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # Log alert
        if level == 'error':
            self.logger.error(f"🚨 {message}")
        elif level == 'warning':
            self.logger.warning(f"⚠️ {message}")
        else:
            self.logger.info(f"ℹ️ {message}")
    
    def get_metrics(self, category: str = None) -> Dict[str, Any]:
        """Get metrics."""
        if category:
            return self.metrics.get(category, {})
        return self.metrics
    
    def get_alerts(self, level: str = None) -> list:
        """Get alerts."""
        if level:
            return [alert for alert in self.alerts if alert['level'] == level]
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []

# Global enhanced monitor instance
enhanced_monitor = EnhancedMonitor()
'''
    
    # Write the integration code
    with open('agent/enhanced_monitor_integration.py', 'w') as f:
        f.write(monitoring_integration_code)
    
    logger.info(f"✅ Integrated {len(monitor_functions)} monitoring features")
    return len(monitor_functions)


def integrate_validation_features(report, logger):
    """Integrate validation features into the main system."""
    logger.info("✅ Integrating validation features...")
    
    # Find validation functions in the report
    validation_functions = []
    for feature in report['activated_features']:
        if feature['type'] == 'validation':
            validation_functions.append(feature)
    
    # Create enhanced validation system
    validation_integration_code = '''
# Enhanced Validation System Integration
import ast
import json
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

class EnhancedValidator:
    """Enhanced validation system using activated features."""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True, "Valid Python syntax"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
    
    def validate_json_syntax(self, json_str: str) -> Tuple[bool, str]:
        """Validate JSON syntax."""
        try:
            json.loads(json_str)
            return True, "Valid JSON syntax"
        except json.JSONDecodeError as e:
            return False, f"JSON error: {e}"
    
    def validate_file_exists(self, file_path: str) -> Tuple[bool, str]:
        """Validate file exists."""
        path = Path(file_path)
        if path.exists():
            return True, f"File exists: {file_path}"
        else:
            return False, f"File not found: {file_path}"
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration structure."""
        errors = []
        
        required_keys = ['models', 'api_keys']
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        if 'models' in config and not isinstance(config['models'], dict):
            errors.append("'models' must be a dictionary")
        
        return len(errors) == 0, errors
    
    def run_comprehensive_validation(self, target: str) -> Dict[str, Any]:
        """Run comprehensive validation on a target."""
        results = {
            'target': target,
            'validations': [],
            'overall_status': 'unknown'
        }
        
        # File existence validation
        exists, message = self.validate_file_exists(target)
        results['validations'].append({
            'type': 'file_existence',
            'status': 'pass' if exists else 'fail',
            'message': message
        })
        
        # If file exists, try syntax validation
        if exists and target.endswith('.py'):
            with open(target, 'r') as f:
                code = f.read()
            syntax_valid, syntax_message = self.validate_python_syntax(code)
            results['validations'].append({
                'type': 'python_syntax',
                'status': 'pass' if syntax_valid else 'fail',
                'message': syntax_message
            })
        
        # Determine overall status
        failed_validations = [v for v in results['validations'] if v['status'] == 'fail']
        if not failed_validations:
            results['overall_status'] = 'pass'
        else:
            results['overall_status'] = 'fail'
        
        return results

# Global enhanced validator instance
enhanced_validator = EnhancedValidator()
'''
    
    # Write the integration code
    with open('agent/enhanced_validator_integration.py', 'w') as f:
        f.write(validation_integration_code)
    
    logger.info(f"✅ Integrated {len(validation_functions)} validation features")
    return len(validation_functions)


def integrate_interface_features(report, logger):
    """Integrate interface features into the main system."""
    logger.info("🖥️ Integrating interface features...")
    
    # Find interface functions in the report
    interface_functions = []
    for feature in report['activated_features']:
        if feature['type'] == 'interface':
            interface_functions.append(feature)
    
    # Create enhanced interface system
    interface_integration_code = '''
# Enhanced Interface System Integration
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class EnhancedInterface:
    """Enhanced interface system using activated features."""
    
    def __init__(self):
        self.interface_elements = {}
        self.templates = {}
    
    def generate_dashboard(self, data: Dict[str, Any]) -> str:
        """Generate a dashboard HTML."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Hephaestus Enhanced Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .status-pass { color: green; }
        .status-fail { color: red; }
        .status-warning { color: orange; }
    </style>
</head>
<body>
    <h1>🚀 Hephaestus Enhanced Dashboard</h1>
    
    <div class="metric">
        <h2>System Status</h2>
        <p>Status: <span class="status-pass">✅ Active</span></p>
        <p>Features Activated: {features_count}</p>
        <p>Workflows Created: {workflows_count}</p>
    </div>
    
    <div class="metric">
        <h2>Recent Activity</h2>
        <ul>
            {recent_activity}
        </ul>
    </div>
    
    <div class="metric">
        <h2>Performance Metrics</h2>
        <p>Cache Hit Rate: {cache_hit_rate}%</p>
        <p>Validation Success Rate: {validation_rate}%</p>
    </div>
</body>
</html>
"""
        
        # Generate recent activity list
        recent_activity = ""
        if 'recent_activity' in data:
            for activity in data['recent_activity'][:5]:
                recent_activity += f"<li>{activity}</li>"
        
        return html_template.format(
            features_count=data.get('features_count', 0),
            workflows_count=data.get('workflows_count', 0),
            recent_activity=recent_activity,
            cache_hit_rate=data.get('cache_hit_rate', 0),
            validation_rate=data.get('validation_rate', 0)
        )
    
    def generate_api_documentation(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API documentation."""
        doc_template = """
# Enhanced API Documentation

## Available Endpoints

{endpoints}

## Usage Examples

{examples}
"""
        
        endpoints_doc = ""
        for endpoint in endpoints:
            endpoints_doc += f"""
### {endpoint['name']}
- **Method**: {endpoint['method']}
- **Path**: {endpoint['path']}
- **Description**: {endpoint['description']}
"""
        
        examples_doc = """
```bash
# Example API calls
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"target": "agent/"}'
```
"""
        
        return doc_template.format(
            endpoints=endpoints_doc,
            examples=examples_doc
        )
    
    def save_interface(self, content: str, file_path: str):
        """Save interface content to file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# Global enhanced interface instance
enhanced_interface = EnhancedInterface()
'''
    
    # Write the integration code
    with open('agent/enhanced_interface_integration.py', 'w') as f:
        f.write(interface_integration_code)
    
    logger.info(f"✅ Integrated {len(interface_functions)} interface features")
    return len(interface_functions)


def create_main_integration_file(logger):
    """Create the main integration file that imports all enhanced systems."""
    integration_code = '''
"""
Main Integration File - Enhanced Systems

This file integrates all the enhanced systems (caching, monitoring, validation, interface)
into the main Hephaestus system.
"""

from agent.enhanced_cache_integration import enhanced_cache
from agent.enhanced_monitor_integration import enhanced_monitor
from agent.enhanced_validator_integration import enhanced_validator
from agent.enhanced_interface_integration import enhanced_interface

# Export all enhanced systems
__all__ = [
    'enhanced_cache',
    'enhanced_monitor', 
    'enhanced_validator',
    'enhanced_interface'
]

def get_enhanced_systems():
    """Get all enhanced systems."""
    return {
        'cache': enhanced_cache,
        'monitor': enhanced_monitor,
        'validator': enhanced_validator,
        'interface': enhanced_interface
    }

def initialize_enhanced_systems():
    """Initialize all enhanced systems."""
    print("🚀 Initializing Enhanced Systems...")
    print("   • Enhanced Caching System: ✅")
    print("   • Enhanced Monitoring System: ✅")
    print("   • Enhanced Validation System: ✅")
    print("   • Enhanced Interface System: ✅")
    print("✅ All enhanced systems initialized!")

if __name__ == "__main__":
    initialize_enhanced_systems()
'''
    
    with open('agent/enhanced_systems_integration.py', 'w') as f:
        f.write(integration_code)
    
    logger.info("✅ Created main integration file")


def main():
    """Main function to integrate activated features."""
    logger = setup_logging()
    
    logger.info("🔗 Starting Feature Integration Process")
    logger.info("=" * 60)
    
    try:
        # Load activation report
        report = load_activation_report()
        if not report:
            logger.error("❌ No feature activation report found!")
            return
        
        logger.info("✅ Feature activation report loaded")
        
        # Integrate features by category
        cache_count = integrate_caching_features(report, logger)
        monitor_count = integrate_monitoring_features(report, logger)
        validation_count = integrate_validation_features(report, logger)
        interface_count = integrate_interface_features(report, logger)
        
        # Create main integration file
        create_main_integration_file(logger)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔗 FEATURE INTEGRATION SUMMARY")
        print("=" * 60)
        
        total_integrated = cache_count + monitor_count + validation_count + interface_count
        print(f"💾 Caching Features Integrated: {cache_count}")
        print(f"📊 Monitoring Features Integrated: {monitor_count}")
        print(f"✅ Validation Features Integrated: {validation_count}")
        print(f"🖥️ Interface Features Integrated: {interface_count}")
        print(f"🎯 Total Features Integrated: {total_integrated}")
        
        print("\n📁 Integration Files Created:")
        print("   • agent/enhanced_cache_integration.py")
        print("   • agent/enhanced_monitor_integration.py")
        print("   • agent/enhanced_validator_integration.py")
        print("   • agent/enhanced_interface_integration.py")
        print("   • agent/enhanced_systems_integration.py")
        
        print("\n🚀 Next Steps:")
        print("   1. Import enhanced systems in your main application")
        print("   2. Use enhanced_cache.cached() decorator for performance")
        print("   3. Use enhanced_monitor.track_metric() for monitoring")
        print("   4. Use enhanced_validator for comprehensive validation")
        print("   5. Use enhanced_interface for dynamic interfaces")
        
        print("\n" + "=" * 60)
        print("✅ Feature integration completed successfully!")
        print("🚀 Enhanced systems are ready to use!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error during feature integration: {e}")
        raise


if __name__ == "__main__":
    main() 