import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


class CapabilityGapDetector:
    """
    Analyzes failure patterns and evolution history to detect when the agent
    needs to develop new capabilities rather than just fixing code.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.gap_detection_history = []
        self.known_capabilities = set()
        self.failure_patterns = defaultdict(list)
        
    def analyze_capability_gaps(self, 
                              memory_data: Dict[str, Any],
                              capabilities_content: str,
                              roadmap_content: str,
                              evolution_log_path: str = "logs/evolution_log.csv") -> Dict[str, Any]:
        """
        Analyze historical data to identify capability gaps.
        
        Args:
            memory_data: Historical memory data
            capabilities_content: Content of CAPABILITIES.md
            roadmap_content: Content of ROADMAP.md
            evolution_log_path: Path to evolution log
            
        Returns:
            Analysis results with detected gaps and recommendations
        """
        self.logger.info("CapabilityGapDetector: Starting capability gap analysis...")
        
        # Parse current capabilities
        current_capabilities = self._parse_capabilities(capabilities_content)
        
        # Analyze failure patterns
        failure_analysis = self._analyze_failure_patterns(memory_data, evolution_log_path)
        
        # Detect capability gaps
        detected_gaps = self._detect_gaps(failure_analysis, current_capabilities, roadmap_content)
        
        # Prioritize gaps
        prioritized_gaps = self._prioritize_gaps(detected_gaps, failure_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(prioritized_gaps, current_capabilities)
        
        analysis_results = {
            "current_capabilities": current_capabilities,
            "failure_analysis": failure_analysis,
            "detected_gaps": detected_gaps,
            "prioritized_gaps": prioritized_gaps,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self.gap_detection_history.append(analysis_results)
        
        self.logger.info(f"CapabilityGapDetector: Found {len(detected_gaps)} capability gaps")
        return analysis_results
    
    def _parse_capabilities(self, capabilities_content: str) -> Dict[str, Any]:
        """Parse CAPABILITIES.md to extract current capabilities."""
        capabilities = {
            "current": [],
            "desired": [],
            "categories": {
                "analysis": [],
                "execution": [],
                "meta_cognition": [],
                "infrastructure": []
            }
        }
        
        # Extract current capabilities
        current_section = re.search(r'## 1\. Capacidades Atuais(.*?)## 2\. Capacidades Desejadas', 
                                   capabilities_content, re.DOTALL)
        if current_section:
            current_text = current_section.group(1)
            
            # Extract subsections
            subsections = re.findall(r'### (.*?)\n(.*?)(?=### |\Z)', current_text, re.DOTALL)
            for title, content in subsections:
                capabilities["current"].append({
                    "title": title.strip(),
                    "content": content.strip()
                })
        
        # Extract desired capabilities
        desired_section = re.search(r'## 2\. Capacidades Desejadas(.*?)$', 
                                   capabilities_content, re.DOTALL)
        if desired_section:
            desired_text = desired_section.group(1)
            
            # Extract subsections
            subsections = re.findall(r'### (.*?)\n(.*?)(?=### |\Z)', desired_text, re.DOTALL)
            for title, content in subsections:
                capabilities["desired"].append({
                    "title": title.strip(),
                    "content": content.strip()
                })
        
        return capabilities
    
    def _analyze_failure_patterns(self, memory_data: Dict[str, Any], evolution_log_path: str) -> Dict[str, Any]:
        """Analyze patterns in failures to identify systemic issues."""
        failure_analysis = {
            "recurring_failures": [],
            "failure_categories": Counter(),
            "temporal_patterns": {},
            "error_types": Counter(),
            "objective_failure_patterns": defaultdict(list)
        }
        
        # Analyze memory data
        failed_objectives = memory_data.get("failed_objectives", [])
        
        for failure in failed_objectives:
            objective = failure.get("objective", "")
            reason = failure.get("reason", "")
            timestamp = failure.get("timestamp", "")
            
            # Categorize failure
            failure_category = self._categorize_failure(reason)
            failure_analysis["failure_categories"][failure_category] += 1
            
            # Track error types
            error_type = self._extract_error_type(reason)
            failure_analysis["error_types"][error_type] += 1
            
            # Group by objective patterns
            objective_pattern = self._extract_objective_pattern(objective)
            failure_analysis["objective_failure_patterns"][objective_pattern].append({
                "objective": objective,
                "reason": reason,
                "timestamp": timestamp
            })
        
        # Identify recurring failures
        for pattern, failures in failure_analysis["objective_failure_patterns"].items():
            if len(failures) >= 2:  # Recurring if happens 2+ times
                failure_analysis["recurring_failures"].append({
                    "pattern": pattern,
                    "count": len(failures),
                    "failures": failures
                })
        
        return failure_analysis
    
    def _categorize_failure(self, reason: str) -> str:
        """Categorize failure based on reason."""
        reason_lower = reason.lower()
        
        if any(keyword in reason_lower for keyword in ["syntax", "parse", "invalid"]):
            return "syntax_error"
        elif any(keyword in reason_lower for keyword in ["test", "pytest", "assertion"]):
            return "test_failure"
        elif any(keyword in reason_lower for keyword in ["timeout", "network", "api"]):
            return "external_dependency"
        elif any(keyword in reason_lower for keyword in ["validation", "strategy"]):
            return "validation_failure"
        elif any(keyword in reason_lower for keyword in ["tool", "command", "execution"]):
            return "tool_failure"
        elif any(keyword in reason_lower for keyword in ["capability", "missing", "not implemented"]):
            return "capability_gap"
        else:
            return "unknown_error"
    
    def _extract_error_type(self, reason: str) -> str:
        """Extract specific error type from reason."""
        # Look for common error patterns
        error_patterns = {
            "ImportError": "import_error",
            "ModuleNotFoundError": "module_not_found",
            "AttributeError": "attribute_error",
            "TypeError": "type_error",
            "ValueError": "value_error",
            "FileNotFoundError": "file_not_found",
            "SYNTAX_VALIDATION_FAILED": "syntax_validation",
            "PYTEST_FAILURE": "pytest_failure",
            "TIMEOUT": "timeout_error"
        }
        
        for pattern, error_type in error_patterns.items():
            if pattern in reason:
                return error_type
        
        return "unknown_error"
    
    def _extract_objective_pattern(self, objective: str) -> str:
        """Extract pattern from objective for grouping similar objectives."""
        # Normalize objective to identify patterns
        objective_lower = objective.lower()
        
        # Common patterns
        if "create" in objective_lower and "test" in objective_lower:
            return "test_creation"
        elif "refactor" in objective_lower:
            return "refactoring"
        elif "implement" in objective_lower:
            return "implementation"
        elif "fix" in objective_lower or "correct" in objective_lower:
            return "error_correction"
        elif "improve" in objective_lower:
            return "improvement"
        elif "add" in objective_lower:
            return "feature_addition"
        elif "update" in objective_lower:
            return "update"
        else:
            return "other"
    
    def _detect_gaps(self, failure_analysis: Dict[str, Any], 
                    current_capabilities: Dict[str, Any], 
                    roadmap_content: str) -> List[Dict[str, Any]]:
        """Detect capability gaps based on failure patterns."""
        detected_gaps = []
        
        # Gap 1: Recurring failures of the same type
        for recurring_failure in failure_analysis["recurring_failures"]:
            if recurring_failure["count"] >= 3:  # 3+ failures of same pattern
                detected_gaps.append({
                    "type": "recurring_failure_pattern",
                    "pattern": recurring_failure["pattern"],
                    "count": recurring_failure["count"],
                    "priority": "high",
                    "description": f"Pattern '{recurring_failure['pattern']}' has failed {recurring_failure['count']} times",
                    "suggested_capability": self._suggest_capability_for_pattern(recurring_failure["pattern"])
                })
        
        # Gap 2: High frequency of specific error types
        for error_type, count in failure_analysis["error_types"].items():
            if count >= 5:  # 5+ occurrences of same error type
                detected_gaps.append({
                    "type": "frequent_error_type",
                    "error_type": error_type,
                    "count": count,
                    "priority": "medium",
                    "description": f"Error type '{error_type}' occurs frequently ({count} times)",
                    "suggested_capability": self._suggest_capability_for_error_type(error_type)
                })
        
        # Gap 3: Missing capabilities mentioned in roadmap but not implemented
        roadmap_gaps = self._find_roadmap_gaps(roadmap_content, current_capabilities)
        for gap in roadmap_gaps:
            detected_gaps.append({
                "type": "roadmap_gap",
                "capability": gap["capability"],
                "priority": gap["priority"],
                "description": f"Roadmap capability '{gap['capability']}' not yet implemented",
                "suggested_capability": gap["capability"]
            })
        
        # Gap 4: Tool/external dependency failures
        tool_failures = failure_analysis["failure_categories"].get("tool_failure", 0)
        external_failures = failure_analysis["failure_categories"].get("external_dependency", 0)
        
        if tool_failures + external_failures >= 3:
            detected_gaps.append({
                "type": "external_dependency_issues",
                "count": tool_failures + external_failures,
                "priority": "medium",
                "description": "High rate of tool/external dependency failures",
                "suggested_capability": "robust_tool_execution_with_fallbacks"
            })
        
        return detected_gaps
    
    def _suggest_capability_for_pattern(self, pattern: str) -> str:
        """Suggest capability needed for a specific failure pattern."""
        capability_map = {
            "test_creation": "intelligent_test_generation",
            "refactoring": "semantic_code_refactoring",
            "implementation": "context_aware_implementation",
            "error_correction": "advanced_error_diagnosis",
            "improvement": "performance_optimization",
            "feature_addition": "feature_planning_and_design"
        }
        
        return capability_map.get(pattern, f"enhanced_{pattern}_capability")
    
    def _suggest_capability_for_error_type(self, error_type: str) -> str:
        """Suggest capability needed for a specific error type."""
        capability_map = {
            "import_error": "dependency_management",
            "module_not_found": "package_resolution",
            "syntax_validation": "advanced_syntax_checking",
            "pytest_failure": "test_debugging_and_fixing",
            "timeout_error": "performance_optimization"
        }
        
        return capability_map.get(error_type, f"enhanced_{error_type}_handling")
    
    def _find_roadmap_gaps(self, roadmap_content: str, current_capabilities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find capabilities mentioned in roadmap but not yet implemented."""
        gaps = []
        
        # Extract roadmap items marked as "Não iniciado"
        not_started_pattern = r'-\s*\[\s*\]\s*\*\*(.*?)\*\*:(.*?)Status:\s*Não iniciado'
        matches = re.findall(not_started_pattern, roadmap_content, re.DOTALL)
        
        for capability, description in matches:
            gaps.append({
                "capability": capability.strip(),
                "description": description.strip(),
                "priority": "medium"
            })
        
        return gaps
    
    def _prioritize_gaps(self, detected_gaps: List[Dict[str, Any]], 
                        failure_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize capability gaps based on impact and frequency."""
        
        # Sort by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        prioritized = sorted(detected_gaps, key=lambda x: (
            priority_order.get(x.get("priority", "low"), 1),
            x.get("count", 0)
        ), reverse=True)
        
        return prioritized
    
    def _generate_recommendations(self, prioritized_gaps: List[Dict[str, Any]], 
                                current_capabilities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations for addressing capability gaps."""
        recommendations = []
        
        for gap in prioritized_gaps[:5]:  # Top 5 gaps
            if gap["priority"] == "high":
                recommendations.append({
                    "gap": gap,
                    "action": "immediate_development",
                    "objective": f"[CAPABILITY DEVELOPMENT] Develop {gap['suggested_capability']} to address recurring {gap['type']}",
                    "estimated_effort": "high",
                    "dependencies": self._identify_dependencies(gap["suggested_capability"])
                })
            elif gap["priority"] == "medium":
                recommendations.append({
                    "gap": gap,
                    "action": "planned_development",
                    "objective": f"[CAPABILITY ENHANCEMENT] Enhance system to handle {gap['type']} better",
                    "estimated_effort": "medium",
                    "dependencies": self._identify_dependencies(gap["suggested_capability"])
                })
        
        return recommendations
    
    def _identify_dependencies(self, capability: str) -> List[str]:
        """Identify dependencies for implementing a capability."""
        # Simple dependency mapping
        dependency_map = {
            "intelligent_test_generation": ["code_analysis", "test_frameworks"],
            "semantic_code_refactoring": ["ast_manipulation", "code_understanding"],
            "advanced_error_diagnosis": ["error_pattern_analysis", "debugging_tools"],
            "dependency_management": ["package_analysis", "version_resolution"],
            "robust_tool_execution_with_fallbacks": ["process_management", "error_handling"]
        }
        
        return dependency_map.get(capability, [])
    
    def generate_capability_development_objective(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Generate a specific objective for developing a missing capability."""
        recommendations = analysis_results.get("recommendations", [])
        
        if not recommendations:
            return None
        
        # Pick the highest priority recommendation
        top_recommendation = recommendations[0]
        
        return top_recommendation.get("objective")
    
    def should_develop_capability(self, analysis_results: Dict[str, Any]) -> bool:
        """Determine if capability development is needed based on analysis."""
        high_priority_gaps = [
            gap for gap in analysis_results.get("prioritized_gaps", [])
            if gap.get("priority") == "high"
        ]
        
        return len(high_priority_gaps) > 0 