"""
Dependency Fixer Agent

Automatically detects and fixes import errors, missing classes, and dependency issues
"""
import re
import ast
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("DependencyFixerAgent")

class DependencyFixerAgent:
    """Agent that automatically fixes import and dependency issues"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.primary_model = config.get("primary_model", "deepseek/deepseek-chat-v3-0324:free")
        self.fallback_model = config.get("fallback_model", "mistralai/mistral-7b-instruct:free")
        logger.info("🔧 Dependency Fixer Agent initialized")
    
    def analyze_import_errors(self, error_log: str) -> List[Dict[str, Any]]:
        """Analyze import errors from test failures or logs"""
        issues = []
        
        # Pattern to match ImportError messages
        import_error_pattern = r"ImportError.*cannot import name '(\w+)' from '([^']+)'"
        matches = re.findall(import_error_pattern, error_log)
        
        for missing_class, module_path in matches:
            issues.append({
                "type": "missing_class",
                "missing_class": missing_class,
                "module_path": module_path,
                "severity": "high"
            })
        
        # Pattern to match ModuleNotFoundError
        module_error_pattern = r"ModuleNotFoundError.*No module named '([^']+)'"
        module_matches = re.findall(module_error_pattern, error_log)
        
        for missing_module in module_matches:
            issues.append({
                "type": "missing_module",
                "missing_module": missing_module,
                "severity": "high"
            })
        
        return issues
    
    def scan_file_for_missing_classes(self, file_path: str, required_classes: List[str]) -> List[str]:
        """Scan a file to see which required classes are missing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file to find class definitions
            tree = ast.parse(content)
            defined_classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    defined_classes.append(node.name)
            
            missing_classes = [cls for cls in required_classes if cls not in defined_classes]
            return missing_classes
            
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return required_classes
    
    def generate_missing_class_code(self, class_name: str, context: str) -> str:
        """Generate code for a missing class based on context"""
        prompt = f"""
        Generate a Pydantic class definition for '{class_name}' based on the context.
        
        Context: {context}
        
        Requirements:
        1. Use Pydantic BaseModel
        2. Include appropriate type hints
        3. Add docstring
        4. Make fields optional with sensible defaults where appropriate
        5. Follow Python best practices
        
        Generate only the class definition, no imports or other code.
        """
        
        # This would normally call the LLM, but for now we'll use a template
        templates = {
            "SelfReflectionRequest": '''
class SelfReflectionRequest(BaseModel):
    """Pydantic model for deep_self_reflection endpoint request"""
    introspection_depth: float = 0.5
    include_meta_awareness: bool = True
    include_cognitive_state: bool = True
''',
            "AwarenessReportRequest": '''
class AwarenessReportRequest(BaseModel):
    """Pydantic model for self_awareness_report endpoint request"""
    include_metrics: bool = True
    include_trajectory: bool = True
    include_insights: bool = True
''',
            "ValidationRequest": '''
class ValidationRequest(BaseModel):
    """Pydantic model for validation endpoint request"""
    data: Dict[str, Any]
    endpoint: str
    strict_validation: bool = True
'''
        }
        
        return templates.get(class_name, f'''
class {class_name}(BaseModel):
    """Pydantic model for {class_name.lower()}"""
    # TODO: Add appropriate fields based on context
    pass
''')
    
    def fix_import_issues(self, issues: List[Dict[str, Any]], project_root: str = ".") -> List[Dict[str, Any]]:
        """Fix import issues by adding missing classes or modules"""
        fixes_applied = []
        
        for issue in issues:
            if issue["type"] == "missing_class":
                fix_result = self._fix_missing_class(issue, project_root)
                if fix_result:
                    fixes_applied.append(fix_result)
            
            elif issue["type"] == "missing_module":
                fix_result = self._fix_missing_module(issue, project_root)
                if fix_result:
                    fixes_applied.append(fix_result)
        
        return fixes_applied
    
    def _fix_missing_class(self, issue: Dict[str, Any], project_root: str) -> Optional[Dict[str, Any]]:
        """Fix a missing class by adding it to the appropriate module"""
        missing_class = issue["missing_class"]
        module_path = issue["module_path"]
        
        # Convert module path to file path
        file_path = Path(project_root) / module_path.replace(".", "/") + ".py"
        
        if not file_path.exists():
            logger.warning(f"Module file not found: {file_path}")
            return None
        
        # Check if class is actually missing
        missing_classes = self.scan_file_for_missing_classes(str(file_path), [missing_class])
        
        if missing_class not in missing_classes:
            logger.info(f"Class {missing_class} already exists in {file_path}")
            return None
        
        # Generate the missing class code
        class_code = self.generate_missing_class_code(missing_class, f"Module: {module_path}")
        
        # Add the class to the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find a good place to insert the class (after imports, before existing classes)
            lines = content.split('\n')
            insert_index = 0
            
            # Find the first class definition
            for i, line in enumerate(lines):
                if line.strip().startswith('class '):
                    insert_index = i
                    break
            else:
                # If no classes found, insert after imports
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_index = i + 1
            
            # Insert the new class
            lines.insert(insert_index, class_code)
            new_content = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"✅ Added missing class {missing_class} to {file_path}")
            
            return {
                "type": "class_added",
                "class_name": missing_class,
                "file_path": str(file_path),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error fixing missing class {missing_class}: {e}")
            return None
    
    def _fix_missing_module(self, issue: Dict[str, Any], project_root: str) -> Optional[Dict[str, Any]]:
        """Fix a missing module by creating it"""
        missing_module = issue["missing_module"]
        
        # Create the module file
        module_path = Path(project_root) / missing_module.replace(".", "/") + ".py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(f'''
"""
{missing_module}

Auto-generated module by DependencyFixerAgent
"""
from typing import Dict, Any

# TODO: Add appropriate imports and classes
''')
            
            logger.info(f"✅ Created missing module {missing_module} at {module_path}")
            
            return {
                "type": "module_created",
                "module_name": missing_module,
                "file_path": str(module_path),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error creating missing module {missing_module}: {e}")
            return None
    
    def run_analysis(self, error_logs: str, project_root: str = ".") -> Dict[str, Any]:
        """Run complete dependency analysis and fixing"""
        logger.info("🔍 Starting dependency analysis...")
        
        # Analyze import errors
        issues = self.analyze_import_errors(error_logs)
        
        if not issues:
            logger.info("✅ No import issues found")
            return {
                "issues_found": 0,
                "fixes_applied": 0,
                "success": True
            }
        
        logger.info(f"🔧 Found {len(issues)} import issues")
        
        # Apply fixes
        fixes_applied = self.fix_import_issues(issues, project_root)
        
        logger.info(f"✅ Applied {len(fixes_applied)} fixes")
        
        return {
            "issues_found": len(issues),
            "fixes_applied": len(fixes_applied),
            "issues": issues,
            "fixes": fixes_applied,
            "success": len(fixes_applied) > 0
        } 