import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import ast
import re

from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response
from hephaestus.utils.project_scanner import analyze_code_metrics


class SelfReflectionAgent:
    """
    Agent that analyzes the Hephaestus codebase itself to identify patterns,
    inefficiencies, and opportunities for self-improvement.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.reflection_history = []
    
    def analyze_self_code(self, target_modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Performs deep analysis of the Hephaestus codebase to identify improvement opportunities.
        
        Args:
            target_modules: Specific modules to analyze. If None, analyzes core modules.
            
        Returns:
            Analysis results with identified patterns and improvement suggestions.
        """
        self.logger.info("SelfReflectionAgent: Starting self-code analysis...")
        
        if target_modules is None:
            target_modules = [
                "agent/brain.py",
                "agent/agents/architect_agent.py", 
                "agent/agents/maestro_agent.py",
                "agent/agents/error_analyzer.py",
                "agent/cycle_runner.py",
                "agent/hephaestus_agent.py"
            ]
        
        analysis_results = {
            "code_patterns": [],
            "inefficiencies": [],
            "improvement_opportunities": [],
            "architectural_insights": [],
            "meta_insights": []
        }
        
        # Analyze each target module
        for module_path in target_modules:
            if Path(module_path).exists():
                module_analysis = self._analyze_module(module_path)
                analysis_results["code_patterns"].extend(module_analysis.get("patterns", []))
                analysis_results["inefficiencies"].extend(module_analysis.get("inefficiencies", []))
                analysis_results["improvement_opportunities"].extend(module_analysis.get("opportunities", []))
        
        # Cross-module architectural analysis
        arch_insights = self._analyze_architecture_patterns(target_modules)
        analysis_results["architectural_insights"] = arch_insights
        
        # Meta-analysis: analyze our own analysis patterns
        meta_insights = self._meta_analyze_reflection_patterns()
        analysis_results["meta_insights"] = meta_insights
        
        # Store reflection for future meta-analysis
        self.reflection_history.append(analysis_results)
        
        self.logger.info(f"SelfReflectionAgent: Analysis complete. Found {len(analysis_results['improvement_opportunities'])} improvement opportunities.")
        return analysis_results
    
    def _analyze_module(self, module_path: str) -> Dict[str, Any]:
        """Analyzes a single module for patterns and opportunities."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Parse AST for structural analysis
            tree = ast.parse(code_content)
            
            # Basic metrics
            metrics = self._extract_module_metrics(tree, code_content)
            
            # Pattern detection
            patterns = self._detect_code_patterns(code_content, tree)
            
            # Inefficiency detection
            inefficiencies = self._detect_inefficiencies(code_content, tree, module_path)
            
            # Improvement opportunities
            opportunities = self._identify_improvement_opportunities(code_content, tree, module_path, metrics)
            
            return {
                "module": module_path,
                "metrics": metrics,
                "patterns": patterns,
                "inefficiencies": inefficiencies,
                "opportunities": opportunities
            }
            
        except Exception as e:
            self.logger.error(f"SelfReflectionAgent: Error analyzing module {module_path}: {e}")
            return {"module": module_path, "error": str(e)}
    
    def _extract_module_metrics(self, tree: ast.AST, code_content: str) -> Dict[str, Any]:
        """Extract basic metrics from module."""
        metrics = {
            "total_lines": len(code_content.split('\n')),
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "docstrings": 0,
            "complexity_hotspots": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions"] += 1
                # Check for docstring
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    metrics["docstrings"] += 1
                # Simple complexity check (nested loops, conditionals)
                complexity = self._calculate_simple_complexity(node)
                if complexity > 10:  # Arbitrary threshold
                    metrics["complexity_hotspots"].append({
                        "function": node.name,
                        "complexity": complexity,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics["imports"] += 1
        
        return metrics
    
    def _calculate_simple_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate simple complexity score for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _detect_code_patterns(self, code_content: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect recurring patterns in code."""
        patterns = []
        
        # Pattern 1: Repetitive error handling
        error_handling_pattern = re.findall(r'except.*?:\s*\n\s*self\.logger\.error', code_content, re.DOTALL)
        if len(error_handling_pattern) > 3:
            patterns.append({
                "type": "repetitive_error_handling",
                "occurrences": len(error_handling_pattern),
                "suggestion": "Consider creating a common error handling decorator or utility"
            })
        
        # Pattern 2: LLM call patterns
        llm_call_pattern = re.findall(r'call_llm_api\(.*?\)', code_content, re.DOTALL)
        if len(llm_call_pattern) > 2:
            patterns.append({
                "type": "multiple_llm_calls",
                "occurrences": len(llm_call_pattern),
                "suggestion": "Consider standardizing LLM call patterns or creating a higher-level abstraction"
            })
        
        # Pattern 3: JSON parsing patterns
        json_parse_pattern = re.findall(r'parse_json_response\(.*?\)', code_content)
        if len(json_parse_pattern) > 1:
            patterns.append({
                "type": "json_parsing_pattern",
                "occurrences": len(json_parse_pattern),
                "suggestion": "JSON parsing pattern is well-abstracted"
            })
        
        return patterns
    
    def _detect_inefficiencies(self, code_content: str, tree: ast.AST, module_path: str) -> List[Dict[str, Any]]:
        """Detect potential inefficiencies."""
        inefficiencies = []
        
        # Check for string concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add):
                        # Potential string concatenation in loop
                        inefficiencies.append({
                            "type": "potential_string_concat_in_loop",
                            "line": child.lineno,
                            "module": module_path,
                            "suggestion": "Consider using list join or string formatting"
                        })
        
        # Check for repeated file operations
        file_ops = re.findall(r'open\(.*?\)', code_content)
        if len(file_ops) > 5:
            inefficiencies.append({
                "type": "multiple_file_operations",
                "occurrences": len(file_ops),
                "module": module_path,
                "suggestion": "Consider caching or batching file operations"
            })
        
        return inefficiencies
    
    def _identify_improvement_opportunities(self, code_content: str, tree: ast.AST, 
                                         module_path: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific improvement opportunities."""
        opportunities = []
        
        # Large function opportunity
        for hotspot in metrics.get("complexity_hotspots", []):
            if hotspot["complexity"] > 15:
                opportunities.append({
                    "type": "function_refactoring",
                    "priority": "high",
                    "module": module_path,
                    "function": hotspot["function"],
                    "line": hotspot["line"],
                    "suggestion": f"Function '{hotspot['function']}' has high complexity ({hotspot['complexity']}). Consider breaking it into smaller functions."
                })
        
        # Documentation opportunity
        if metrics["functions"] > 0 and metrics["docstrings"] / metrics["functions"] < 0.5:
            opportunities.append({
                "type": "documentation_improvement",
                "priority": "medium",
                "module": module_path,
                "suggestion": f"Only {metrics['docstrings']}/{metrics['functions']} functions have docstrings. Consider improving documentation."
            })
        
        # Agent-specific opportunities
        if "agents/" in module_path:
            # Check for common agent patterns
            if "temperature" in code_content and "0.2" in code_content:
                opportunities.append({
                    "type": "hardcoded_parameters",
                    "priority": "medium",
                    "module": module_path,
                    "suggestion": "Consider making LLM parameters configurable rather than hardcoded"
                })
        
        return opportunities
    
    def _analyze_architecture_patterns(self, target_modules: List[str]) -> List[Dict[str, Any]]:
        """Analyze cross-module architectural patterns."""
        insights = []
        
        # Check for circular dependencies or tight coupling
        import_patterns = {}
        for module_path in target_modules:
            if Path(module_path).exists():
                try:
                    with open(module_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract imports
                    imports = re.findall(r'from\s+(agent\.[^\s]+)\s+import', content)
                    imports.extend(re.findall(r'import\s+(agent\.[^\s]+)', content))
                    import_patterns[module_path] = imports
                except Exception as e:
                    self.logger.warning(f"Could not analyze imports for {module_path}: {e}")
        
        # Analyze coupling
        if len(import_patterns) > 1:
            insights.append({
                "type": "coupling_analysis",
                "import_patterns": import_patterns,
                "suggestion": "Monitor import dependencies to ensure loose coupling"
            })
        
        # Check for agent communication patterns
        agent_modules = [m for m in target_modules if "agents/" in m]
        if len(agent_modules) > 2:
            insights.append({
                "type": "agent_collaboration",
                "agent_count": len(agent_modules),
                "suggestion": "Consider standardizing agent communication patterns and interfaces"
            })
        
        return insights
    
    def _meta_analyze_reflection_patterns(self) -> List[Dict[str, Any]]:
        """Analyze patterns in our own reflection history."""
        meta_insights = []
        
        if len(self.reflection_history) >= 2:
            # Compare recent reflections to identify trends
            recent_opportunities = [r.get("improvement_opportunities", []) for r in self.reflection_history[-3:]]
            
            # Count recurring opportunity types
            opportunity_types = {}
            for opportunities in recent_opportunities:
                for opp in opportunities:
                    opp_type = opp.get("type", "unknown")
                    opportunity_types[opp_type] = opportunity_types.get(opp_type, 0) + 1
            
            # Identify persistent issues
            persistent_issues = [ot for ot, count in opportunity_types.items() if count >= 2]
            
            if persistent_issues:
                meta_insights.append({
                    "type": "persistent_improvement_opportunities",
                    "issues": persistent_issues,
                    "suggestion": "These improvement opportunities keep appearing. Consider prioritizing them for systematic resolution."
                })
        
        return meta_insights
    
    def generate_self_improvement_objective(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """
        Generate a concrete objective for self-improvement based on analysis.
        """
        opportunities = analysis_results.get("improvement_opportunities", [])
        if not opportunities:
            return None
        
        # Prioritize high-priority opportunities
        high_priority = [opp for opp in opportunities if opp.get("priority") == "high"]
        target_opp = high_priority[0] if high_priority else opportunities[0]
        
        if target_opp["type"] == "function_refactoring":
            return f"[SELF-IMPROVEMENT] Refactor function '{target_opp['function']}' in {target_opp['module']} to reduce complexity from {target_opp.get('complexity', 'high')} by breaking it into smaller, more focused functions."
        
        elif target_opp["type"] == "documentation_improvement":
            return f"[SELF-IMPROVEMENT] Improve documentation in {target_opp['module']} by adding comprehensive docstrings to all public functions and classes."
        
        elif target_opp["type"] == "hardcoded_parameters":
            return f"[SELF-IMPROVEMENT] Make hardcoded parameters in {target_opp['module']} configurable by moving them to the configuration system."
        
        # Default case
        return f"[SELF-IMPROVEMENT] Address {target_opp['type']} in {target_opp.get('module', 'system')}: {target_opp.get('suggestion', 'Improve code quality')}"
    
    def create_self_improvement_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for the ArchitectAgent to implement self-improvements.
        """
        prompt_parts = [
            "[SELF-IMPROVEMENT CONTEXT]",
            "The SelfReflectionAgent has analyzed the Hephaestus codebase and identified improvement opportunities.",
            "Your task is to implement these improvements to enhance the system's capabilities and efficiency.",
            ""
        ]
        
        # Add analysis summary
        opportunities = analysis_results.get("improvement_opportunities", [])
        inefficiencies = analysis_results.get("inefficiencies", [])
        
        if opportunities:
            prompt_parts.extend([
                "[IMPROVEMENT OPPORTUNITIES]",
                json.dumps(opportunities, indent=2),
                ""
            ])
        
        if inefficiencies:
            prompt_parts.extend([
                "[IDENTIFIED INEFFICIENCIES]", 
                json.dumps(inefficiencies, indent=2),
                ""
            ])
        
        # Add architectural insights
        arch_insights = analysis_results.get("architectural_insights", [])
        if arch_insights:
            prompt_parts.extend([
                "[ARCHITECTURAL INSIGHTS]",
                json.dumps(arch_insights, indent=2),
                ""
            ])
        
        prompt_parts.extend([
            "[INSTRUCTIONS]",
            "1. Focus on the highest priority improvements first",
            "2. Ensure changes maintain backward compatibility",
            "3. Add appropriate tests for any new functionality",
            "4. Update documentation as needed",
            "5. Consider the impact on other system components",
            "",
            "Generate patches to implement these self-improvements systematically."
        ])
        
        return "\n".join(prompt_parts) 