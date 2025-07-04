import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import re
import hashlib

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


class PromptOptimizer:
    """
    Analyzes prompt performance and automatically optimizes prompts
    for better results. This is a core RSI capability.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.prompt_performance_history = {}
        self.optimization_history = []
        self.prompt_versions = defaultdict(list)
        
    def analyze_prompt_performance(self, 
                                 memory_data: Dict[str, Any],
                                 evolution_log_path: str = "evolution_log.csv") -> Dict[str, Any]:
        """
        Analyze the performance of prompts used by different agents.
        
        Args:
            memory_data: Historical memory data with objective outcomes
            evolution_log_path: Path to evolution log for additional metrics
            
        Returns:
            Analysis of prompt performance patterns
        """
        self.logger.info("PromptOptimizer: Analyzing prompt performance...")
        
        performance_analysis = {
            "agent_performance": {},
            "strategy_performance": {},
            "prompt_patterns": {},
            "failure_correlations": [],
            "optimization_opportunities": []
        }
        
        # Analyze agent performance patterns
        agent_performance = self._analyze_agent_performance(memory_data)
        performance_analysis["agent_performance"] = agent_performance
        
        # Analyze strategy performance
        strategy_performance = self._analyze_strategy_performance(memory_data)
        performance_analysis["strategy_performance"] = strategy_performance
        
        # Identify prompt patterns
        prompt_patterns = self._identify_prompt_patterns(memory_data)
        performance_analysis["prompt_patterns"] = prompt_patterns
        
        # Find failure correlations
        failure_correlations = self._find_failure_correlations(memory_data, agent_performance)
        performance_analysis["failure_correlations"] = failure_correlations
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            agent_performance, strategy_performance, failure_correlations
        )
        performance_analysis["optimization_opportunities"] = optimization_opportunities
        
        self.logger.info(f"PromptOptimizer: Found {len(optimization_opportunities)} optimization opportunities")
        return performance_analysis
    
    def _analyze_agent_performance(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance patterns for each agent type."""
        agent_stats = defaultdict(lambda: {
            "total_objectives": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "common_failures": Counter(),
            "recent_trend": "stable"
        })
        
        # Analyze completed objectives
        completed = memory_data.get("completed_objectives", [])
        for obj in completed:
            # Infer agent involvement from objective type
            agent_type = self._infer_agent_from_objective(obj.get("objective", ""))
            agent_stats[agent_type]["total_objectives"] += 1
            agent_stats[agent_type]["successful"] += 1
        
        # Analyze failed objectives
        failed = memory_data.get("failed_objectives", [])
        for obj in failed:
            agent_type = self._infer_agent_from_objective(obj.get("objective", ""))
            reason = obj.get("reason", "")
            
            agent_stats[agent_type]["total_objectives"] += 1
            agent_stats[agent_type]["failed"] += 1
            agent_stats[agent_type]["common_failures"][reason] += 1
        
        # Calculate success rates
        for agent_type, stats in agent_stats.items():
            if stats["total_objectives"] > 0:
                stats["success_rate"] = stats["successful"] / stats["total_objectives"]
        
        return dict(agent_stats)
    
    def _infer_agent_from_objective(self, objective: str) -> str:
        """Infer which agent was likely involved based on objective content."""
        objective_lower = objective.lower()
        
        if any(keyword in objective_lower for keyword in ["patch", "implement", "create", "modify"]):
            return "ArchitectAgent"
        elif any(keyword in objective_lower for keyword in ["strategy", "validation", "choose"]):
            return "MaestroAgent"
        elif any(keyword in objective_lower for keyword in ["error", "fix", "debug", "correct"]):
            return "ErrorAnalysisAgent"
        elif any(keyword in objective_lower for keyword in ["performance", "analyze", "metrics"]):
            return "PerformanceAnalysisAgent"
        elif any(keyword in objective_lower for keyword in ["self", "improve", "reflection"]):
            return "SelfReflectionAgent"
        else:
            return "GeneralAgent"
    
    def _analyze_strategy_performance(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance of different validation strategies."""
        strategy_stats = defaultdict(lambda: {
            "uses": 0,
            "successes": 0,
            "failures": 0,
            "success_rate": 0.0,
            "failure_reasons": Counter()
        })
        
        # This would ideally come from evolution_log.csv
        # For now, we'll extract from memory data patterns
        
        failed_objectives = memory_data.get("failed_objectives", [])
        for failure in failed_objectives:
            reason = failure.get("reason", "")
            
            # Try to infer strategy from failure reason
            strategy = self._infer_strategy_from_failure(reason)
            strategy_stats[strategy]["uses"] += 1
            strategy_stats[strategy]["failures"] += 1
            strategy_stats[strategy]["failure_reasons"][reason] += 1
        
        # Calculate success rates
        for strategy, stats in strategy_stats.items():
            if stats["uses"] > 0:
                stats["success_rate"] = stats["successes"] / stats["uses"]
        
        return dict(strategy_stats)
    
    def _infer_strategy_from_failure(self, reason: str) -> str:
        """Infer which validation strategy was used based on failure reason."""
        reason_lower = reason.lower()
        
        if "syntax" in reason_lower:
            return "syntax_validation"
        elif "pytest" in reason_lower or "test" in reason_lower:
            return "pytest_validation"
        elif "sandbox" in reason_lower:
            return "sandbox_validation"
        elif "timeout" in reason_lower:
            return "timeout_strategy"
        else:
            return "unknown_strategy"
    
    def _identify_prompt_patterns(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns in prompt effectiveness."""
        patterns = {
            "high_success_patterns": [],
            "low_success_patterns": [],
            "complexity_correlation": {},
            "time_patterns": {}
        }
        
        # Analyze objective complexity vs success
        objectives = []
        objectives.extend(memory_data.get("completed_objectives", []))
        objectives.extend(memory_data.get("failed_objectives", []))
        
        for obj in objectives:
            objective_text = obj.get("objective", "")
            complexity = self._calculate_objective_complexity(objective_text)
            success = obj in memory_data.get("completed_objectives", [])
            
            if complexity not in patterns["complexity_correlation"]:
                patterns["complexity_correlation"][complexity] = {"total": 0, "successes": 0}
            
            patterns["complexity_correlation"][complexity]["total"] += 1
            if success:
                patterns["complexity_correlation"][complexity]["successes"] += 1
        
        # Identify successful patterns
        for complexity, stats in patterns["complexity_correlation"].items():
            success_rate = stats["successes"] / stats["total"] if stats["total"] > 0 else 0
            if success_rate > 0.8 and stats["total"] >= 3:
                patterns["high_success_patterns"].append({
                    "pattern": f"complexity_{complexity}",
                    "success_rate": success_rate,
                    "sample_size": stats["total"]
                })
            elif success_rate < 0.3 and stats["total"] >= 3:
                patterns["low_success_patterns"].append({
                    "pattern": f"complexity_{complexity}",
                    "success_rate": success_rate,
                    "sample_size": stats["total"]
                })
        
        return patterns
    
    def _calculate_objective_complexity(self, objective: str) -> str:
        """Calculate complexity level of an objective."""
        word_count = len(objective.split())
        
        # Count complexity indicators
        complex_keywords = ["refactor", "implement", "analyze", "optimize", "enhance"]
        simple_keywords = ["add", "create", "fix", "update", "change"]
        
        complex_count = sum(1 for keyword in complex_keywords if keyword in objective.lower())
        simple_count = sum(1 for keyword in simple_keywords if keyword in objective.lower())
        
        if word_count > 20 or complex_count >= 2:
            return "high"
        elif word_count > 10 or complex_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _find_failure_correlations(self, memory_data: Dict[str, Any], 
                                 agent_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find correlations between failures and prompt characteristics."""
        correlations = []
        
        # Correlation 1: Agent success rate vs objective complexity
        for agent_type, stats in agent_performance.items():
            if stats["success_rate"] < 0.5 and stats["total_objectives"] >= 5:
                correlations.append({
                    "type": "low_success_rate",
                    "agent": agent_type,
                    "success_rate": stats["success_rate"],
                    "sample_size": stats["total_objectives"],
                    "main_failures": list(stats["common_failures"].most_common(3))
                })
        
        # Correlation 2: Recurring failure patterns
        failed_objectives = memory_data.get("failed_objectives", [])
        failure_reasons = Counter([obj.get("reason", "") for obj in failed_objectives])
        
        for reason, count in failure_reasons.most_common(5):
            if count >= 3:  # Recurring failure
                correlations.append({
                    "type": "recurring_failure",
                    "reason": reason,
                    "count": count,
                    "percentage": count / len(failed_objectives) if failed_objectives else 0
                })
        
        return correlations
    
    def _identify_optimization_opportunities(self, 
                                           agent_performance: Dict[str, Any],
                                           strategy_performance: Dict[str, Any],
                                           failure_correlations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify specific opportunities for prompt optimization."""
        opportunities = []
        
        # Opportunity 1: Low-performing agents need prompt refinement
        for agent_type, stats in agent_performance.items():
            if stats["success_rate"] < 0.6 and stats["total_objectives"] >= 3:
                opportunities.append({
                    "type": "agent_prompt_optimization",
                    "agent": agent_type,
                    "current_success_rate": stats["success_rate"],
                    "priority": "high" if stats["success_rate"] < 0.4 else "medium",
                    "suggested_improvements": self._suggest_prompt_improvements(agent_type, stats),
                    "estimated_impact": "20-40% success rate improvement"
                })
        
        # Opportunity 2: Strategy-specific optimizations
        for strategy, stats in strategy_performance.items():
            if stats["success_rate"] < 0.5 and stats["uses"] >= 3:
                opportunities.append({
                    "type": "strategy_optimization",
                    "strategy": strategy,
                    "current_success_rate": stats["success_rate"],
                    "priority": "medium",
                    "main_failure_reasons": list(stats["failure_reasons"].most_common(3)),
                    "estimated_impact": "15-30% success rate improvement"
                })
        
        # Opportunity 3: Recurring failure pattern fixes
        for correlation in failure_correlations:
            if correlation["type"] == "recurring_failure" and correlation["count"] >= 5:
                opportunities.append({
                    "type": "failure_pattern_fix",
                    "failure_reason": correlation["reason"],
                    "frequency": correlation["count"],
                    "priority": "high",
                    "suggested_approach": self._suggest_failure_fix_approach(correlation["reason"]),
                    "estimated_impact": "Eliminate 80% of this failure type"
                })
        
        return opportunities
    
    def _suggest_prompt_improvements(self, agent_type: str, stats: Dict[str, Any]) -> List[str]:
        """Suggest specific prompt improvements for an agent."""
        improvements = []
        
        common_failures = stats.get("common_failures", {})
        
        if agent_type == "ArchitectAgent":
            if any("syntax" in failure for failure in common_failures.keys()):
                improvements.append("Add explicit syntax validation instructions")
                improvements.append("Include more code examples in prompts")
            if any("patch" in failure for failure in common_failures.keys()):
                improvements.append("Clarify patch format requirements")
                improvements.append("Add step-by-step patch creation guidance")
        
        elif agent_type == "MaestroAgent":
            improvements.append("Improve strategy selection criteria")
            improvements.append("Add more context about validation trade-offs")
            improvements.append("Include historical strategy performance data")
        
        elif agent_type == "ErrorAnalysisAgent":
            improvements.append("Enhance error categorization instructions")
            improvements.append("Add more specific recovery strategies")
            improvements.append("Include context about previous similar errors")
        
        # Generic improvements
        improvements.append("Add clearer output format specifications")
        improvements.append("Include more detailed examples")
        improvements.append("Add explicit error handling instructions")
        
        return improvements
    
    def _suggest_failure_fix_approach(self, failure_reason: str) -> str:
        """Suggest approach to fix a recurring failure pattern."""
        reason_lower = failure_reason.lower()
        
        if "syntax" in reason_lower:
            return "Enhance pre-validation in ArchitectAgent prompts with syntax checking guidance"
        elif "timeout" in reason_lower:
            return "Add time estimation and optimization instructions to relevant agent prompts"
        elif "test" in reason_lower or "pytest" in reason_lower:
            return "Improve test-related instructions in ArchitectAgent and add test debugging guidance"
        elif "validation" in reason_lower:
            return "Review and optimize MaestroAgent strategy selection prompts"
        else:
            return "Add specific handling instructions for this error type in relevant agent prompts"
    
    def generate_optimized_prompt(self, 
                                agent_type: str, 
                                current_prompt: str,
                                performance_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate an optimized version of a prompt based on performance analysis.
        
        Args:
            agent_type: Type of agent (ArchitectAgent, MaestroAgent, etc.)
            current_prompt: Current prompt text
            performance_analysis: Results from analyze_prompt_performance
            
        Returns:
            Optimized prompt with rationale
        """
        self.logger.info(f"PromptOptimizer: Generating optimized prompt for {agent_type}")
        
        # Find optimization opportunities for this agent
        opportunities = [
            opp for opp in performance_analysis.get("optimization_opportunities", [])
            if opp.get("agent") == agent_type or opp.get("type") == "failure_pattern_fix"
        ]
        
        if not opportunities:
            self.logger.info(f"No optimization opportunities found for {agent_type}")
            return None
        
        # Create optimization prompt for LLM
        optimization_prompt = self._create_optimization_prompt(
            agent_type, current_prompt, opportunities, performance_analysis
        )
        
        # Call LLM to generate optimized prompt
        optimized_response, error = call_llm_api(
            model_config=self.model_config,
            prompt=optimization_prompt,
            temperature=0.3,  # Lower temperature for more focused optimization
            logger=self.logger
        )
        
        if error:
            self.logger.error(f"PromptOptimizer: LLM call failed: {error}")
            return None
        
        # Parse response
        parsed_response, parse_error = parse_json_response(optimized_response, self.logger)
        
        if parse_error or not parsed_response:
            self.logger.error(f"PromptOptimizer: Failed to parse optimization response")
            return None
        
        # Create prompt version tracking
        prompt_hash = hashlib.md5(current_prompt.encode()).hexdigest()[:8]
        optimized_hash = hashlib.md5(parsed_response.get("optimized_prompt", "").encode()).hexdigest()[:8]
        
        optimization_result = {
            "agent_type": agent_type,
            "original_prompt_hash": prompt_hash,
            "optimized_prompt_hash": optimized_hash,
            "optimized_prompt": parsed_response.get("optimized_prompt"),
            "optimization_rationale": parsed_response.get("rationale"),
            "key_changes": parsed_response.get("key_changes", []),
            "expected_improvements": parsed_response.get("expected_improvements", []),
            "optimization_timestamp": datetime.now().isoformat(),
            "based_on_opportunities": opportunities
        }
        
        # Store in optimization history
        self.optimization_history.append(optimization_result)
        
        # Store prompt version
        self.prompt_versions[agent_type].append({
            "prompt": parsed_response.get("optimized_prompt"),
            "hash": optimized_hash,
            "timestamp": datetime.now().isoformat(),
            "performance_baseline": None  # Will be filled after testing
        })
        
        self.logger.info(f"PromptOptimizer: Generated optimized prompt for {agent_type}")
        return optimization_result
    
    def _create_optimization_prompt(self, 
                                  agent_type: str,
                                  current_prompt: str,
                                  opportunities: List[Dict[str, Any]],
                                  performance_analysis: Dict[str, Any]) -> str:
        """Create prompt for LLM to optimize another prompt."""
        
        prompt_parts = [
            "[PROMPT OPTIMIZATION TASK]",
            f"You are optimizing a prompt for {agent_type} in the Hephaestus autonomous agent system.",
            "Your goal is to improve the prompt's effectiveness based on performance analysis.",
            "",
            "[CURRENT PROMPT]",
            current_prompt,
            "",
            "[PERFORMANCE ANALYSIS]",
            json.dumps(performance_analysis.get("agent_performance", {}).get(agent_type, {}), indent=2),
            "",
            "[OPTIMIZATION OPPORTUNITIES]",
            json.dumps(opportunities, indent=2),
            "",
            "[OPTIMIZATION GUIDELINES]",
            "1. Maintain the core functionality and output format",
            "2. Add clarity and specificity where needed",
            "3. Include better examples and edge case handling",
            "4. Address the specific failure patterns identified",
            "5. Make instructions more actionable and unambiguous",
            "6. Ensure backwards compatibility with existing system",
            "",
            "[REQUIRED OUTPUT FORMAT]",
            "Respond with a JSON object containing:",
            "{",
            '  "optimized_prompt": "The improved prompt text",',
            '  "rationale": "Explanation of why changes were made",',
            '  "key_changes": ["List of specific changes made"],',
            '  "expected_improvements": ["Expected performance improvements"]',
            "}"
        ]
        
        return "\n".join(prompt_parts)
    
    def create_optimization_objective(self, performance_analysis: Dict[str, Any]) -> Optional[str]:
        """Create an objective for the agent to optimize its own prompts."""
        opportunities = performance_analysis.get("optimization_opportunities", [])
        
        if not opportunities:
            return None
        
        # Focus on highest priority opportunity
        high_priority = [opp for opp in opportunities if opp.get("priority") == "high"]
        target_opp = high_priority[0] if high_priority else opportunities[0]
        
        if target_opp["type"] == "agent_prompt_optimization":
            return f"[PROMPT OPTIMIZATION] Optimize {target_opp['agent']} prompts to improve success rate from {target_opp['current_success_rate']:.1%} using identified performance patterns and failure analysis."
        
        elif target_opp["type"] == "failure_pattern_fix":
            return f"[PROMPT ENHANCEMENT] Enhance agent prompts to prevent recurring '{target_opp['failure_reason']}' failures (occurs {target_opp['frequency']} times)."
        
        else:
            return f"[PROMPT IMPROVEMENT] Improve system prompts to address {target_opp['type']} based on performance analysis." 