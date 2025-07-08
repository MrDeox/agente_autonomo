"""
Unified Validation System - Comprehensive validation for Hephaestus
"""

import re
import ast
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import subprocess
import importlib.util

from hephaestus.utils.logger_factory import LoggerFactory
from hephaestus.utils.config_manager import ConfigManager


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    status: str  # passed, failed, warning, skipped
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "medium"  # low, medium, high, critical
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ValidationSuite:
    """Collection of validation results."""
    name: str
    results: List[ValidationResult]
    overall_status: str
    passed: int
    failed: int
    warnings: int
    skipped: int
    execution_time: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['results'] = [r.to_dict() for r in self.results]
        return data


class UnifiedValidator:
    """
    Comprehensive validation system for the Hephaestus platform.
    
    Features:
    - Code syntax and structure validation
    - Configuration validation
    - Agent interface compliance
    - Performance checks
    - Security validation
    - Integration testing
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_component_logger("UnifiedValidator")
        
        # Validation configuration
        self.config = ConfigManager.get_config_value("validation", {})
        self.strict_mode = self.config.get("strict_mode", False)
        self.timeout = self.config.get("timeout", 300)  # 5 minutes
        
        # Validation rules
        self.syntax_rules = self._load_syntax_rules()
        self.security_rules = self._load_security_rules()
        self.performance_thresholds = self._load_performance_thresholds()
        
        # State
        self.validation_history: List[ValidationSuite] = []
        
        self.logger.info("✅ Unified Validator initialized")
    
    async def validate_system(self, scope: str = "full") -> ValidationSuite:
        """
        Validate the entire system or specific scope.
        
        Args:
            scope: Validation scope - 'full', 'code', 'config', 'agents', 'security'
            
        Returns:
            ValidationSuite with all results
        """
        start_time = asyncio.get_event_loop().time()
        
        self.logger.info(f"🔍 Starting {scope} system validation")
        
        results = []
        
        try:
            if scope in ["full", "code"]:
                results.extend(await self._validate_code_structure())
                results.extend(await self._validate_syntax())
            
            if scope in ["full", "config"]:
                results.extend(await self._validate_configuration())
            
            if scope in ["full", "agents"]:
                results.extend(await self._validate_agents())
            
            if scope in ["full", "security"]:
                results.extend(await self._validate_security())
            
            if scope in ["full"]:
                results.extend(await self._validate_integration())
                results.extend(await self._validate_performance())
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            results.append(ValidationResult(
                check_name="validation_error",
                status="failed",
                message=f"Validation system error: {str(e)}",
                severity="critical"
            ))
        
        # Calculate summary
        passed = len([r for r in results if r.status == "passed"])
        failed = len([r for r in results if r.status == "failed"])
        warnings = len([r for r in results if r.status == "warning"])
        skipped = len([r for r in results if r.status == "skipped"])
        
        # Determine overall status
        if failed > 0:
            if any(r.severity == "critical" for r in results if r.status == "failed"):
                overall_status = "critical"
            else:
                overall_status = "failed"
        elif warnings > 0:
            overall_status = "warning"
        else:
            overall_status = "passed"
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        suite = ValidationSuite(
            name=f"{scope}_validation",
            results=results,
            overall_status=overall_status,
            passed=passed,
            failed=failed,
            warnings=warnings,
            skipped=skipped,
            execution_time=execution_time
        )
        
        # Store in history
        self.validation_history.append(suite)
        
        self.logger.info(f"✅ Validation completed: {overall_status} "
                        f"({passed} passed, {failed} failed, {warnings} warnings)")
        
        return suite
    
    async def _validate_code_structure(self) -> List[ValidationResult]:
        """Validate code structure and organization."""
        results = []
        
        # Check for required directories
        required_dirs = ["src/hephaestus", "tests", "config"]
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                results.append(ValidationResult(
                    check_name=f"directory_{dir_path.replace('/', '_')}",
                    status="passed",
                    message=f"Required directory {dir_path} exists"
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"directory_{dir_path.replace('/', '_')}",
                    status="failed",
                    message=f"Missing required directory: {dir_path}",
                    severity="high"
                ))
        
        # Check for critical files
        critical_files = [
            "src/hephaestus/__init__.py",
            "src/hephaestus/core/__init__.py",
            "src/hephaestus/agents/__init__.py"
        ]
        
        for file_path in critical_files:
            if Path(file_path).exists():
                results.append(ValidationResult(
                    check_name=f"file_{file_path.replace('/', '_').replace('.', '_')}",
                    status="passed",
                    message=f"Critical file {file_path} exists"
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"file_{file_path.replace('/', '_').replace('.', '_')}",
                    status="failed",
                    message=f"Missing critical file: {file_path}",
                    severity="critical"
                ))
        
        return results
    
    async def _validate_syntax(self) -> List[ValidationResult]:
        """Validate Python syntax for all Python files."""
        results = []
        
        python_files = list(Path("src").rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse with AST
                ast.parse(content)
                
                results.append(ValidationResult(
                    check_name=f"syntax_{file_path.name}",
                    status="passed",
                    message=f"Syntax valid: {file_path}",
                    severity="low"
                ))
                
            except SyntaxError as e:
                results.append(ValidationResult(
                    check_name=f"syntax_{file_path.name}",
                    status="failed",
                    message=f"Syntax error in {file_path}: {e}",
                    details={"line": e.lineno, "error": str(e)},
                    severity="high"
                ))
                
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"syntax_{file_path.name}",
                    status="warning",
                    message=f"Could not parse {file_path}: {e}",
                    severity="medium"
                ))
        
        return results
    
    async def _validate_configuration(self) -> List[ValidationResult]:
        """Validate configuration files."""
        results = []
        
        # Check YAML files
        yaml_files = list(Path("config").rglob("*.yaml")) + list(Path("config").rglob("*.yml"))
        
        for file_path in yaml_files:
            try:
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                
                results.append(ValidationResult(
                    check_name=f"yaml_{file_path.name}",
                    status="passed",
                    message=f"Valid YAML: {file_path}"
                ))
                
            except yaml.YAMLError as e:
                results.append(ValidationResult(
                    check_name=f"yaml_{file_path.name}",
                    status="failed",
                    message=f"Invalid YAML in {file_path}: {e}",
                    severity="high"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"yaml_{file_path.name}",
                    status="warning",
                    message=f"Could not read {file_path}: {e}"
                ))
        
        # Check JSON files
        json_files = list(Path(".").rglob("*.json"))[:20]  # Limit to prevent overwhelming
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                
                results.append(ValidationResult(
                    check_name=f"json_{file_path.name}",
                    status="passed",
                    message=f"Valid JSON: {file_path}"
                ))
                
            except json.JSONDecodeError as e:
                results.append(ValidationResult(
                    check_name=f"json_{file_path.name}",
                    status="failed",
                    message=f"Invalid JSON in {file_path}: {e}",
                    severity="medium"
                ))
            except Exception:
                # Skip files that can't be read
                continue
        
        return results
    
    async def _validate_agents(self) -> List[ValidationResult]:
        """Validate agent implementations."""
        results = []
        
        # Find all agent files
        agent_files = list(Path("src/hephaestus/agents").glob("*_agent.py"))
        agent_files.extend(list(Path("src/hephaestus/agents").glob("*_enhanced.py")))
        
        for file_path in agent_files:
            try:
                # Read and parse the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Check for required patterns
                has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
                has_execute_method = any(
                    isinstance(node, ast.FunctionDef) and node.name == "execute"
                    for node in ast.walk(tree)
                )
                
                if has_class:
                    results.append(ValidationResult(
                        check_name=f"agent_class_{file_path.stem}",
                        status="passed",
                        message=f"Agent {file_path.stem} has class definition"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"agent_class_{file_path.stem}",
                        status="failed",
                        message=f"Agent {file_path.stem} missing class definition",
                        severity="high"
                    ))
                
                if has_execute_method:
                    results.append(ValidationResult(
                        check_name=f"agent_execute_{file_path.stem}",
                        status="passed",
                        message=f"Agent {file_path.stem} has execute method"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"agent_execute_{file_path.stem}",
                        status="warning",
                        message=f"Agent {file_path.stem} missing execute method"
                    ))
                
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"agent_parse_{file_path.stem}",
                    status="failed",
                    message=f"Could not validate agent {file_path.stem}: {e}",
                    severity="medium"
                ))
        
        return results
    
    async def _validate_security(self) -> List[ValidationResult]:
        """Validate security aspects."""
        results = []
        
        # Check for common security issues
        python_files = list(Path("src").rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for security patterns
                for rule_name, rule_data in self.security_rules.items():
                    pattern = rule_data["pattern"]
                    severity = rule_data["severity"]
                    message = rule_data["message"]
                    
                    if re.search(pattern, content, re.IGNORECASE):
                        results.append(ValidationResult(
                            check_name=f"security_{rule_name}_{file_path.stem}",
                            status="warning" if severity == "low" else "failed",
                            message=f"{message} in {file_path}",
                            severity=severity
                        ))
                
            except Exception:
                # Skip files that can't be read
                continue
        
        return results
    
    async def _validate_integration(self) -> List[ValidationResult]:
        """Validate system integration."""
        results = []
        
        try:
            # Test imports
            test_imports = [
                "hephaestus.core",
                "hephaestus.agents",
                "hephaestus.utils",
                "hephaestus.monitoring"
            ]
            
            for import_name in test_imports:
                try:
                    spec = importlib.util.find_spec(import_name)
                    if spec is not None:
                        results.append(ValidationResult(
                            check_name=f"import_{import_name.replace('.', '_')}",
                            status="passed",
                            message=f"Module {import_name} can be imported"
                        ))
                    else:
                        results.append(ValidationResult(
                            check_name=f"import_{import_name.replace('.', '_')}",
                            status="failed",
                            message=f"Module {import_name} cannot be imported",
                            severity="high"
                        ))
                except Exception as e:
                    results.append(ValidationResult(
                        check_name=f"import_{import_name.replace('.', '_')}",
                        status="failed",
                        message=f"Import error for {import_name}: {e}",
                        severity="medium"
                    ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="integration_test",
                status="failed",
                message=f"Integration validation error: {e}",
                severity="high"
            ))
        
        return results
    
    async def _validate_performance(self) -> List[ValidationResult]:
        """Validate performance aspects."""
        results = []
        
        # Check file sizes
        large_files = []
        for file_path in Path("src").rglob("*.py"):
            if file_path.stat().st_size > 50000:  # 50KB
                large_files.append((file_path, file_path.stat().st_size))
        
        if large_files:
            results.append(ValidationResult(
                check_name="large_files",
                status="warning",
                message=f"Found {len(large_files)} large files (>50KB)",
                details={"files": [(str(f), s) for f, s in large_files[:5]]}
            ))
        else:
            results.append(ValidationResult(
                check_name="large_files",
                status="passed",
                message="No excessively large files found"
            ))
        
        # Check complexity (line count as proxy)
        complex_files = []
        for file_path in Path("src").rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                if lines > 500:
                    complex_files.append((file_path, lines))
            except Exception:
                continue
        
        if complex_files:
            results.append(ValidationResult(
                check_name="complex_files",
                status="warning",
                message=f"Found {len(complex_files)} complex files (>500 lines)",
                details={"files": [(str(f), l) for f, l in complex_files[:5]]}
            ))
        else:
            results.append(ValidationResult(
                check_name="complex_files",
                status="passed",
                message="No overly complex files found"
            ))
        
        return results
    
    def _load_syntax_rules(self) -> Dict[str, Any]:
        """Load syntax validation rules."""
        return {
            "unused_imports": {
                "pattern": r"^import\s+\w+$",
                "severity": "low",
                "message": "Potential unused import"
            },
            "long_lines": {
                "pattern": r".{120,}",
                "severity": "low", 
                "message": "Line longer than 120 characters"
            }
        }
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security validation rules."""
        return {
            "hardcoded_password": {
                "pattern": r"password\s*=\s*['\"][^'\"]{3,}['\"]",
                "severity": "high",
                "message": "Potential hardcoded password"
            },
            "sql_injection": {
                "pattern": r"execute\s*\(\s*['\"].*\+.*['\"]",
                "severity": "critical",
                "message": "Potential SQL injection vulnerability"
            },
            "eval_usage": {
                "pattern": r"eval\s*\(",
                "severity": "high",
                "message": "Use of eval() function"
            },
            "pickle_usage": {
                "pattern": r"pickle\.loads?\s*\(",
                "severity": "medium",
                "message": "Use of pickle module"
            }
        }
    
    def _load_performance_thresholds(self) -> Dict[str, Any]:
        """Load performance validation thresholds."""
        return {
            "max_file_size": 100000,  # 100KB
            "max_line_count": 1000,
            "max_function_count": 50,
            "max_class_count": 10
        }
    
    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get validation history."""
        return [suite.to_dict() for suite in self.validation_history[-limit:]]
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of latest validation."""
        if not self.validation_history:
            return {"status": "no_validation", "message": "No validations performed yet"}
        
        latest = self.validation_history[-1]
        
        return {
            "status": latest.overall_status,
            "timestamp": latest.timestamp.isoformat(),
            "passed": latest.passed,
            "failed": latest.failed,
            "warnings": latest.warnings,
            "execution_time": latest.execution_time,
            "critical_issues": len([
                r for r in latest.results 
                if r.status == "failed" and r.severity == "critical"
            ])
        }


# Global validator instance
_validator = None

def get_unified_validator() -> UnifiedValidator:
    """Get the global unified validator instance."""
    global _validator
    if _validator is None:
        _validator = UnifiedValidator()
    return _validator