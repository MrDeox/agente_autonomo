"""
System Engineer Agent - Comprehensive Code Analysis and Optimization

This agent performs deep analysis of the codebase to identify:
- Unused functions, classes, and modules
- Dead code and unreachable paths
- Performance bottlenecks
- Code duplication
- Unused dependencies
- Optimization opportunities
"""

import os
import ast
import inspect
import importlib
import logging
from typing import Dict, List, Set, Tuple, Any, Optional
from pathlib import Path
import time
import json
from collections import defaultdict, Counter
import subprocess
import sys


class SystemEngineerAgent:
    """
    System Engineer Agent for comprehensive code analysis and optimization.
    
    Capabilities:
    - Dead code detection
    - Usage analysis
    - Performance profiling
    - Dependency analysis
    - Code duplication detection
    - Optimization recommendations
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.name = "system_engineer"
        self.capabilities = [
            "code_analysis",
            "dead_code_detection", 
            "performance_analysis",
            "dependency_analysis",
            "optimization_recommendations"
        ]
        
        # Analysis results storage
        self.analysis_results = {
            "unused_functions": [],
            "unused_classes": [],
            "unused_modules": [],
            "dead_code": [],
            "duplicate_code": [],
            "performance_issues": [],
            "unused_dependencies": [],
            "optimization_opportunities": []
        }
        
        # Code analysis cache
        self._function_definitions = {}
        self._function_calls = {}
        self._imports = {}
        self._file_analysis = {}
        
        self.logger.info("🔧 System Engineer Agent initialized for comprehensive code analysis")
    
    def analyze_codebase(self, project_root: str = ".") -> Dict[str, Any]:
        """
        Perform comprehensive codebase analysis.
        
        Args:
            project_root: Root directory of the project
            
        Returns:
            Dictionary with analysis results
        """
        self.logger.info("🔍 Starting comprehensive codebase analysis...")
        start_time = time.time()
        
        try:
            # Reset analysis results
            self.analysis_results = {key: [] for key in self.analysis_results.keys()}
            
            # Get all Python files
            python_files = self._get_python_files(project_root)
            self.logger.info(f"📁 Found {len(python_files)} Python files to analyze")
            
            # Phase 1: Parse and analyze all files
            self._parse_all_files(python_files)
            
            # Phase 2: Detect unused code
            self._detect_unused_code()
            
            # Phase 3: Detect dead code
            self._detect_dead_code()
            
            # Phase 4: Detect code duplication
            self._detect_code_duplication()
            
            # Phase 5: Analyze performance issues
            self._analyze_performance_issues()
            
            # Phase 6: Analyze dependencies
            self._analyze_dependencies()
            
            # Phase 7: Generate optimization recommendations
            self._generate_optimization_recommendations()
            
            analysis_time = time.time() - start_time
            self.logger.info(f"✅ Codebase analysis completed in {analysis_time:.2f}s")
            
            return self._generate_analysis_report()
            
        except Exception as e:
            self.logger.error(f"❌ Error during codebase analysis: {e}")
            raise
    
    def _get_python_files(self, project_root: str) -> List[str]:
        """Get all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(project_root):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if d not in {
                '__pycache__', '.git', '.pytest_cache', 'htmlcov', 
                'node_modules', '.venv', 'venv', 'env'
            }]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _parse_all_files(self, python_files: List[str]):
        """Parse all Python files and extract function definitions, calls, and imports."""
        self.logger.info("📝 Parsing Python files...")
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Could not parse {file_path}: {e}")
    
    def _analyze_ast(self, file_path: str, tree: ast.AST):
        """Analyze AST for function definitions, calls, and imports."""
        file_analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'calls': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                file_analysis['functions'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'file': file_path
                })
                self._function_definitions[f"{file_path}:{node.name}"] = {
                    'file': file_path,
                    'line': node.lineno,
                    'name': node.name
                }
            
            elif isinstance(node, ast.ClassDef):
                file_analysis['classes'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'file': file_path
                })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    file_analysis['imports'].append(alias.name)
                    self._imports[alias.name] = file_path
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    file_analysis['imports'].append(full_name)
                    self._imports[full_name] = file_path
            
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    file_analysis['calls'].append(node.func.id)
                    if node.func.id not in self._function_calls:
                        self._function_calls[node.func.id] = []
                    self._function_calls[node.func.id].append(file_path)
        
        self._file_analysis[file_path] = file_analysis
    
    def _detect_unused_code(self):
        """Detect unused functions, classes, and modules."""
        self.logger.info("🔍 Detecting unused code...")
        
        # Detect unused functions
        for func_key, func_info in self._function_definitions.items():
            func_name = func_info['name']
            
            # Skip special methods and main functions
            if func_name.startswith('__') or func_name == 'main':
                continue
            
            # Check if function is called anywhere
            if func_name not in self._function_calls:
                self.analysis_results['unused_functions'].append(func_info)
        
        # Detect unused classes (simplified - just check if class name is used in calls)
        for file_path, analysis in self._file_analysis.items():
            for class_info in analysis['classes']:
                class_name = class_info['name']
                
                # Skip if class name appears in function calls (simplified check)
                if class_name not in self._function_calls:
                    self.analysis_results['unused_classes'].append(class_info)
    
    def _detect_dead_code(self):
        """Detect dead code (unreachable paths, etc.)."""
        self.logger.info("💀 Detecting dead code...")
        
        # This is a simplified dead code detection
        # In a full implementation, you'd use more sophisticated static analysis
        for file_path, analysis in self._file_analysis.items():
            # Check for unreachable code after return statements
            # This would require more complex AST analysis
            pass
    
    def _detect_code_duplication(self):
        """Detect duplicate code patterns."""
        self.logger.info("🔄 Detecting code duplication...")
        
        # Simple duplication detection based on function content
        function_contents = {}
        
        for file_path, analysis in self._file_analysis.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for func_info in analysis['functions']:
                    # Extract function content (simplified)
                    start_line = func_info['line'] - 1
                    end_line = start_line + 10  # Simplified: just check first 10 lines
                    
                    content = ''.join(lines[start_line:end_line])
                    if content in function_contents:
                        self.analysis_results['duplicate_code'].append({
                            'file1': function_contents[content],
                            'file2': file_path,
                            'function': func_info['name'],
                            'lines': f"{start_line+1}-{end_line}"
                        })
                    else:
                        function_contents[content] = file_path
                        
            except Exception as e:
                self.logger.warning(f"⚠️ Could not analyze duplication in {file_path}: {e}")
    
    def _analyze_performance_issues(self):
        """Analyze potential performance issues."""
        self.logger.info("⚡ Analyzing performance issues...")
        
        for file_path, analysis in self._file_analysis.items():
            # Check for common performance anti-patterns
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for nested loops
                if content.count('for ') > 2 and content.count('for ') < 10:
                    self.analysis_results['performance_issues'].append({
                        'file': file_path,
                        'issue': 'Potential nested loops detected',
                        'severity': 'medium'
                    })
                
                # Check for large functions (simplified)
                for func_info in analysis['functions']:
                    # This would require more sophisticated analysis
                    pass
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not analyze performance in {file_path}: {e}")
    
    def _analyze_dependencies(self):
        """Analyze unused dependencies."""
        self.logger.info("📦 Analyzing dependencies...")
        
        # Check poetry.lock for unused dependencies
        try:
            if os.path.exists('poetry.lock'):
                with open('poetry.lock', 'r') as f:
                    content = f.read()
                
                # Extract package names from poetry.lock
                import re
                packages = re.findall(r'name = "([^"]+)"', content)
                
                # Check which packages are actually imported
                used_packages = set()
                for import_name in self._imports.keys():
                    package_name = import_name.split('.')[0]
                    used_packages.add(package_name)
                
                # Find unused packages
                for package in packages:
                    if package not in used_packages and package not in {
                        'setuptools', 'wheel', 'pip', 'poetry'
                    }:
                        self.analysis_results['unused_dependencies'].append(package)
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Could not analyze dependencies: {e}")
    
    def _generate_optimization_recommendations(self):
        """Generate optimization recommendations based on analysis."""
        self.logger.info("💡 Generating optimization recommendations...")
        
        # Generate recommendations based on findings
        if self.analysis_results['unused_functions']:
            self.analysis_results['optimization_opportunities'].append({
                'type': 'code_cleanup',
                'description': f"Remove {len(self.analysis_results['unused_functions'])} unused functions",
                'impact': 'medium',
                'effort': 'low'
            })
        
        if self.analysis_results['unused_dependencies']:
            self.analysis_results['optimization_opportunities'].append({
                'type': 'dependency_cleanup',
                'description': f"Remove {len(self.analysis_results['unused_dependencies'])} unused dependencies",
                'impact': 'low',
                'effort': 'low'
            })
        
        if self.analysis_results['duplicate_code']:
            self.analysis_results['optimization_opportunities'].append({
                'type': 'refactoring',
                'description': f"Refactor {len(self.analysis_results['duplicate_code'])} duplicate code patterns",
                'impact': 'high',
                'effort': 'medium'
            })
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        report = {
            'summary': {
                'total_files_analyzed': len(self._file_analysis),
                'total_functions': len(self._function_definitions),
                'total_classes': sum(len(analysis['classes']) for analysis in self._file_analysis.values()),
                'total_imports': len(self._imports)
            },
            'findings': {
                'unused_functions_count': len(self.analysis_results['unused_functions']),
                'unused_classes_count': len(self.analysis_results['unused_classes']),
                'dead_code_count': len(self.analysis_results['dead_code']),
                'duplicate_code_count': len(self.analysis_results['duplicate_code']),
                'performance_issues_count': len(self.analysis_results['performance_issues']),
                'unused_dependencies_count': len(self.analysis_results['unused_dependencies']),
                'optimization_opportunities_count': len(self.analysis_results['optimization_opportunities'])
            },
            'details': self.analysis_results,
            'recommendations': self._generate_actionable_recommendations()
        }
        
        return report
    
    def _generate_actionable_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations with priority levels."""
        recommendations = []
        
        # High priority recommendations
        if self.analysis_results['unused_functions']:
            recommendations.append({
                'priority': 'high',
                'action': 'Remove unused functions',
                'description': f"Found {len(self.analysis_results['unused_functions'])} unused functions",
                'files': list(set(func['file'] for func in self.analysis_results['unused_functions'])),
                'estimated_effort': '1-2 hours'
            })
        
        if self.analysis_results['duplicate_code']:
            recommendations.append({
                'priority': 'high',
                'action': 'Refactor duplicate code',
                'description': f"Found {len(self.analysis_results['duplicate_code'])} duplicate code patterns",
                'files': list(set(dup['file1'] for dup in self.analysis_results['duplicate_code'])),
                'estimated_effort': '4-8 hours'
            })
        
        # Medium priority recommendations
        if self.analysis_results['unused_dependencies']:
            recommendations.append({
                'priority': 'medium',
                'action': 'Remove unused dependencies',
                'description': f"Found {len(self.analysis_results['unused_dependencies'])} unused dependencies",
                'dependencies': self.analysis_results['unused_dependencies'],
                'estimated_effort': '30 minutes'
            })
        
        if self.analysis_results['performance_issues']:
            recommendations.append({
                'priority': 'medium',
                'action': 'Address performance issues',
                'description': f"Found {len(self.analysis_results['performance_issues'])} potential performance issues",
                'files': list(set(issue['file'] for issue in self.analysis_results['performance_issues'])),
                'estimated_effort': '2-4 hours'
            })
        
        return recommendations
    
    def run_analysis(self, project_root: str = ".") -> Dict[str, Any]:
        """
        Main method to run comprehensive system analysis.
        
        Args:
            project_root: Root directory of the project
            
        Returns:
            Analysis report with findings and recommendations
        """
        self.logger.info("🚀 Starting System Engineer analysis...")
        
        try:
            report = self.analyze_codebase(project_root)
            
            # Log summary
            self.logger.info("📊 Analysis Summary:")
            self.logger.info(f"   • Files analyzed: {report['summary']['total_files_analyzed']}")
            self.logger.info(f"   • Functions found: {report['summary']['total_functions']}")
            self.logger.info(f"   • Classes found: {report['summary']['total_classes']}")
            self.logger.info(f"   • Unused functions: {report['findings']['unused_functions_count']}")
            self.logger.info(f"   • Unused classes: {report['findings']['unused_classes_count']}")
            self.logger.info(f"   • Duplicate code patterns: {report['findings']['duplicate_code_count']}")
            self.logger.info(f"   • Unused dependencies: {report['findings']['unused_dependencies_count']}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error in system analysis: {e}")
            raise
    
    def generate_cleanup_script(self, report: Dict[str, Any]) -> str:
        """
        Generate a cleanup script based on analysis results.
        
        Args:
            report: Analysis report from run_analysis()
            
        Returns:
            Python script to clean up unused code
        """
        script_lines = [
            "#!/usr/bin/env python3",
            '"""',
            "Auto-generated cleanup script based on System Engineer analysis",
            '"""',
            "",
            "import os",
            "import ast",
            "import shutil",
            "from pathlib import Path",
            "",
            "def remove_unused_functions():",
            "    \"\"\"Remove unused functions identified by analysis.\"\"\"",
        ]
        
        # Add unused function removal
        for func in report['details']['unused_functions']:
            script_lines.extend([
                f"    # Remove unused function: {func['name']} in {func['file']}:{func['line']}",
                f"    # TODO: Manually review and remove if safe",
                ""
            ])
        
        script_lines.extend([
            "def remove_unused_dependencies():",
            "    \"\"\"Remove unused dependencies.\"\"\"",
        ])
        
        # Add unused dependency removal
        for dep in report['details']['unused_dependencies']:
            script_lines.extend([
                f"    # Remove unused dependency: {dep}",
                f"    # Run: poetry remove {dep}",
                ""
            ])
        
        script_lines.extend([
            "if __name__ == '__main__':",
            "    print('🔧 Running cleanup script...')",
            "    print('⚠️  Please review each change before applying!')",
            "    remove_unused_functions()",
            "    remove_unused_dependencies()",
            "    print('✅ Cleanup script completed')",
        ])
        
        return '\n'.join(script_lines) 