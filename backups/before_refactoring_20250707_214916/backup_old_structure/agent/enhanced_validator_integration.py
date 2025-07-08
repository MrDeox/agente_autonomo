
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
