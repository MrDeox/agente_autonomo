"""
Meta-Cognitive Controller for Dynamic LLM Flow Management

This module implements a self-modifying system that can add, remove, or modify
LLM calls based on performance metrics and situational needs.
"""

import ast
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import inspect
import textwrap
from pathlib import Path

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


class FlowModificationType(Enum):
    """Types of modifications the system can make to LLM flows"""
    ADD_CALL = "add_call"
    REMOVE_CALL = "remove_call"
    MERGE_CALLS = "merge_calls"
    SPLIT_CALL = "split_call"
    MODIFY_PROMPT = "modify_prompt"
    CHANGE_MODEL = "change_model"
    ADD_CACHE = "add_cache"
    PARALLELIZE = "parallelize"


@dataclass
class LLMCallPoint:
    """Represents a point in the code where an LLM call is made"""
    file_path: str
    function_name: str
    line_number: int
    call_type: str  # e.g., "architect", "maestro", "review"
    current_prompt: str
    temperature: float
    model_config: Dict[str, Any]
    performance_stats: Dict[str, Any]


@dataclass
class FlowModification:
    """Represents a proposed modification to the LLM flow"""
    modification_type: FlowModificationType
    target_call_point: Optional[LLMCallPoint]
    new_call_point: Optional[LLMCallPoint]
    rationale: str
    expected_improvement: float
    risk_level: str  # "low", "medium", "high"
    implementation_code: str


class MetaCognitiveController:
    """
    Controller that monitors and modifies LLM call flows dynamically.
    This is the brain's brain - it thinks about how the system thinks.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.call_history = []
        self.modification_history = []
        self.performance_baseline = {}
        
    def analyze_current_flow(self) -> Dict[str, Any]:
        """
        Analyze the current LLM call flow to identify optimization opportunities.
        """
        self.logger.info("MetaCognitiveController: Analyzing current LLM flow...")
        
        # Scan codebase for LLM calls
        call_points = self._scan_for_llm_calls()
        
        # Analyze call patterns
        patterns = self._analyze_call_patterns(call_points)
        
        # Identify bottlenecks and inefficiencies
        bottlenecks = self._identify_bottlenecks(patterns)
        
        # Generate optimization opportunities
        opportunities = self._generate_optimization_opportunities(patterns, bottlenecks)
        
        return {
            "call_points": call_points,
            "patterns": patterns,
            "bottlenecks": bottlenecks,
            "opportunities": opportunities,
            "total_calls_per_cycle": len(call_points),
            "estimated_cost_per_cycle": self._estimate_cost(call_points)
        }
    
    def propose_flow_modifications(self, analysis: Dict[str, Any]) -> List[FlowModification]:
        """
        Generate proposed modifications to optimize the LLM call flow.
        
        Args:
            analysis: Current flow analysis from analyze_current_flow()
            
        Returns:
            List[FlowModification]: List of proposed modifications, empty if none found
        """
        self.logger.info("MetaCognitiveController: Proposing flow modifications...")
        
        prompt = self._build_modification_prompt(analysis)
        llm_response = self._get_llm_modification_proposals(prompt)
        
        if not llm_response:
            return []
            
        return self._parse_modification_proposals(llm_response, analysis)

    def _get_llm_modification_proposals(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get modification proposals from LLM."""
        response, error = call_llm_api(
            model_config=self.model_config,
            prompt=prompt,
            temperature=0.4,
            logger=self.logger
        )
        
        if error:
            self.logger.error(f"Failed to get modification proposals: {error}")
            return None
            
        return parse_json_response(response, self.logger)[0]

    def _parse_modification_proposals(self, 
                                    response: Dict[str, Any], 
                                    analysis: Dict[str, Any]) -> List[FlowModification]:
        """Parse LLM response into FlowModification objects."""
        modifications = []
        for prop in response.get("modifications", []):
            mod = self._create_flow_modification(prop, analysis)
            if mod:
                modifications.append(mod)
        return modifications
    
    def implement_modification(self, modification: FlowModification) -> bool:
        """
        Actually implement a proposed modification by modifying the code.
        """
        self.logger.info(f"MetaCognitiveController: Implementing {modification.modification_type.value}")
        
        try:
            if modification.modification_type == FlowModificationType.ADD_CALL:
                return self._implement_add_call(modification)
            elif modification.modification_type == FlowModificationType.REMOVE_CALL:
                return self._implement_remove_call(modification)
            elif modification.modification_type == FlowModificationType.MERGE_CALLS:
                return self._implement_merge_calls(modification)
            elif modification.modification_type == FlowModificationType.ADD_CACHE:
                return self._implement_add_cache(modification)
            elif modification.modification_type == FlowModificationType.PARALLELIZE:
                return self._implement_parallelize(modification)
            else:
                self.logger.warning(f"Modification type {modification.modification_type} not yet implemented")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to implement modification: {e}")
            return False
    
    def _scan_for_llm_calls(self) -> List[LLMCallPoint]:
        """Scan the codebase for all LLM call points."""
        call_points = []
        
        # Define patterns to look for
        llm_call_patterns = [
            "call_llm_api",
            "call_llm_with_fallback",
            "call_gemini_api",
            "call_openrouter_api"
        ]
        
        # Scan key agent files
        agent_files = [
            "agent/brain.py",
            "agent/agents/architect_agent.py",
            "agent/agents/maestro_agent.py",
            "agent/agents/code_review_agent.py",
            "agent/agents/error_analyzer.py",
            "agent/agents/prompt_optimizer.py",
            "agent/agents/self_reflection_agent.py"
        ]
        
        for file_path in agent_files:
            if not Path(file_path).exists():
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Find all function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in llm_call_patterns:
                        # Extract information about this call
                        call_point = self._extract_call_point_info(
                            file_path, node, content
                        )
                        if call_point:
                            call_points.append(call_point)
        
        return call_points
    
    def _analyze_call_patterns(self, call_points: List[LLMCallPoint]) -> Dict[str, Any]:
        """Analyze patterns in LLM calls."""
        patterns = {
            "sequential_calls": [],
            "conditional_calls": [],
            "repeated_similar_calls": [],
            "high_frequency_calls": [],
            "expensive_calls": []
        }
        
        # Group by function
        calls_by_function = {}
        for cp in call_points:
            key = f"{cp.file_path}::{cp.function_name}"
            if key not in calls_by_function:
                calls_by_function[key] = []
            calls_by_function[key].append(cp)
        
        # Identify sequential calls in same function
        for func, calls in calls_by_function.items():
            if len(calls) > 1:
                patterns["sequential_calls"].append({
                    "function": func,
                    "calls": calls,
                    "count": len(calls)
                })
        
        # Identify expensive calls (based on model or token usage)
        for cp in call_points:
            if "gpt-4" in str(cp.model_config) or cp.temperature > 0.7:
                patterns["expensive_calls"].append(cp)
        
        return patterns
    
    def _identify_bottlenecks(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in the LLM flow."""
        bottlenecks = []
        
        # Sequential calls are often bottlenecks
        for seq in patterns.get("sequential_calls", []):
            if seq["count"] > 2:
                bottlenecks.append({
                    "type": "sequential_overload",
                    "location": seq["function"],
                    "severity": "high" if seq["count"] > 3 else "medium",
                    "calls": seq["calls"]
                })
        
        # Expensive calls in tight loops
        for expensive_call in patterns.get("expensive_calls", []):
            if expensive_call.performance_stats.get("call_frequency", 0) > 10:
                bottlenecks.append({
                    "type": "expensive_frequent_call",
                    "location": f"{expensive_call.file_path}::{expensive_call.function_name}",
                    "severity": "high",
                    "call": expensive_call
                })
        
        return bottlenecks
    
    def _generate_optimization_opportunities(self, 
                                           patterns: Dict[str, Any],
                                           bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific optimization opportunities."""
        opportunities = []
        
        # Opportunity: Merge sequential calls
        for seq in patterns.get("sequential_calls", []):
            if seq["count"] >= 2:
                opportunities.append({
                    "type": FlowModificationType.MERGE_CALLS,
                    "target": seq["calls"],
                    "potential_savings": f"{(seq['count']-1) * 100 / seq['count']:.0f}%",
                    "complexity": "medium",
                    "description": f"Merge {seq['count']} sequential LLM calls in {seq['function']}"
                })
        
        # Opportunity: Add caching for repeated calls
        for call in patterns.get("repeated_similar_calls", []):
            opportunities.append({
                "type": FlowModificationType.ADD_CACHE,
                "target": call,
                "potential_savings": "60-80%",
                "complexity": "low",
                "description": f"Add caching to {call.call_type} calls"
            })
        
        # Opportunity: Parallelize independent calls
        if len(patterns.get("sequential_calls", [])) > 1:
            opportunities.append({
                "type": FlowModificationType.PARALLELIZE,
                "target": patterns["sequential_calls"],
                "potential_savings": "40-60% time reduction",
                "complexity": "high",
                "description": "Parallelize independent LLM calls"
            })
        
        return opportunities
    
    def _build_modification_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for LLM to propose modifications."""
        prompt_parts = [
            "[META-COGNITIVE FLOW OPTIMIZATION TASK]",
            "You are analyzing the LLM call flow of an autonomous agent system.",
            "Your goal is to propose modifications that will improve efficiency without sacrificing intelligence.",
            "",
            "[CURRENT FLOW ANALYSIS]",
            f"Total LLM calls per cycle: {analysis['total_calls_per_cycle']}",
            f"Estimated cost per cycle: ${analysis['estimated_cost_per_cycle']:.2f}",
            "",
            "[IDENTIFIED PATTERNS]",
            json.dumps(analysis["patterns"], indent=2),
            "",
            "[BOTTLENECKS]",
            json.dumps(analysis["bottlenecks"], indent=2),
            "",
            "[OPTIMIZATION OPPORTUNITIES]",
            json.dumps(analysis["opportunities"], indent=2),
            "",
            "[YOUR TASK]",
            "Propose specific modifications to the LLM flow. For each modification:",
            "1. Choose the most impactful opportunities",
            "2. Provide implementation details",
            "3. Estimate the improvement",
            "4. Assess the risk",
            "",
            "[OUTPUT FORMAT]",
            "Respond with a JSON object:",
            "{",
            '  "modifications": [',
            '    {',
            '      "type": "merge_calls|add_call|remove_call|add_cache|parallelize",',
            '      "target_function": "function name",',
            '      "target_file": "file path",',
            '      "description": "what this modification does",',
            '      "implementation_strategy": "how to implement it",',
            '      "expected_improvement": 0.25,  // 25% improvement',
            '      "risk_level": "low|medium|high",',
            '      "code_snippet": "example implementation code"',
            '    }',
            '  ]',
            "}"
        ]
        
        return "\n".join(prompt_parts)
    
    def _create_flow_modification(self, proposal: Dict[str, Any], 
                                analysis: Dict[str, Any]) -> Optional[FlowModification]:
        """Create a FlowModification object from a proposal."""
        try:
            mod_type = FlowModificationType(proposal["type"])
            
            # Find target call point
            target_cp = None
            for cp in analysis["call_points"]:
                if (cp.function_name == proposal.get("target_function") and
                    cp.file_path == proposal.get("target_file")):
                    target_cp = cp
                    break
            
            return FlowModification(
                modification_type=mod_type,
                target_call_point=target_cp,
                new_call_point=None,  # Will be created during implementation
                rationale=proposal.get("description", ""),
                expected_improvement=proposal.get("expected_improvement", 0.1),
                risk_level=proposal.get("risk_level", "medium"),
                implementation_code=proposal.get("code_snippet", "")
            )
        except Exception as e:
            self.logger.error(f"Failed to create flow modification: {e}")
            return None
    
    def _implement_add_call(self, modification: FlowModification) -> bool:
        """Implement adding a new LLM call."""
        # This would modify the AST to add a new call
        # For now, we'll create the implementation plan
        self.logger.info("ADD_CALL implementation would modify AST to inject new LLM call")
        return True
    
    def _implement_remove_call(self, modification: FlowModification) -> bool:
        """Implement removing an LLM call."""
        # This would modify the AST to remove a call
        self.logger.info("REMOVE_CALL implementation would modify AST to remove LLM call")
        return True
    
    def _implement_merge_calls(self, modification: FlowModification) -> bool:
        """Implement merging multiple LLM calls into one."""
        # This would combine multiple prompts into one
        self.logger.info("MERGE_CALLS implementation would combine multiple prompts")
        return True
    
    def _implement_add_cache(self, modification: FlowModification) -> bool:
        """Implement adding cache to an LLM call."""
        # This would wrap the call with caching logic
        self.logger.info("ADD_CACHE implementation would add caching wrapper")
        return True
    
    def _implement_parallelize(self, modification: FlowModification) -> bool:
        """Implement parallelizing LLM calls."""
        # This would use asyncio or threading to parallelize
        self.logger.info("PARALLELIZE implementation would add async/threading")
        return True
    
    def _extract_call_point_info(self, file_path: str, node: ast.Call, 
                                content: str) -> Optional[LLMCallPoint]:
        """Extract information about an LLM call point."""
        try:
            # Get function name containing this call
            lines = content.split('\n')
            line_no = node.lineno - 1
            
            # Search backwards for function definition
            func_name = "unknown"
            for i in range(line_no, -1, -1):
                if lines[i].strip().startswith("def "):
                    func_name = lines[i].split("def ")[1].split("(")[0]
                    break
            
            # Extract temperature if present
            temperature = 0.5  # default
            for keyword in node.keywords:
                if keyword.arg == "temperature":
                    if isinstance(keyword.value, ast.Constant):
                        temperature = keyword.value.value
            
            # Create call point
            return LLMCallPoint(
                file_path=file_path,
                function_name=func_name,
                line_number=node.lineno,
                call_type=self._infer_call_type(func_name, file_path),
                current_prompt="",  # Would need more analysis to extract
                temperature=temperature,
                model_config={},  # Would need more analysis
                performance_stats={}  # Would come from monitoring
            )
        except Exception as e:
            self.logger.error(f"Failed to extract call point info: {e}")
            return None
    
    def _infer_call_type(self, func_name: str, file_path: str) -> str:
        """Infer the type of LLM call based on context."""
        if "architect" in file_path.lower():
            return "architect"
        elif "maestro" in file_path.lower():
            return "maestro"
        elif "review" in file_path.lower():
            return "review"
        elif "error" in file_path.lower():
            return "error_analysis"
        else:
            return "general"
    
    def _estimate_cost(self, call_points: List[LLMCallPoint]) -> float:
        """Estimate the cost of all LLM calls per cycle."""
        # Rough estimates based on model and tokens
        cost_per_call = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude": 0.02,
            "default": 0.001
        }
        
        total_cost = 0
        for cp in call_points:
            model = "default"
            for key in cost_per_call:
                if key in str(cp.model_config):
                    model = key
                    break
            total_cost += cost_per_call[model]
        
        return total_cost
    
    def monitor_and_adapt(self) -> None:
        """
        Continuous monitoring and adaptation loop.
        This is the heart of meta-cognitive evolution.
        """
        self.logger.info("MetaCognitiveController: Starting continuous adaptation loop")
        
        while True:
            try:
                # Analyze current flow
                analysis = self.analyze_current_flow()
                
                # Check if optimization is needed
                if self._should_optimize(analysis):
                    # Propose modifications
                    modifications = self.propose_flow_modifications(analysis)
                    
                    # Rank by expected improvement vs risk
                    ranked_mods = self._rank_modifications(modifications)
                    
                    # Implement top modification
                    if ranked_mods:
                        best_mod = ranked_mods[0]
                        if best_mod.risk_level == "low" or self._approve_risky_modification(best_mod):
                            success = self.implement_modification(best_mod)
                            if success:
                                self.modification_history.append(best_mod)
                                self.logger.info(f"Successfully implemented {best_mod.modification_type.value}")
                
                # Sleep before next iteration
                import time
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in adaptation loop: {e}")
                import time
                time.sleep(60)  # Wait a minute on error
    
    def _should_optimize(self, analysis: Dict[str, Any]) -> bool:
        """Determine if optimization is needed."""
        # Optimize if:
        # - Too many calls per cycle (>10)
        # - High cost per cycle (>$0.10)
        # - Significant bottlenecks identified
        
        if analysis["total_calls_per_cycle"] > 10:
            return True
        if analysis["estimated_cost_per_cycle"] > 0.10:
            return True
        if len(analysis["bottlenecks"]) > 2:
            return True
        
        return False
    
    def _rank_modifications(self, modifications: List[FlowModification]) -> List[FlowModification]:
        """Rank modifications by expected value (improvement vs risk)."""
        def score_modification(mod: FlowModification) -> float:
            risk_multiplier = {"low": 1.0, "medium": 0.7, "high": 0.4}.get(mod.risk_level, 0.5)
            return mod.expected_improvement * risk_multiplier
        
        return sorted(modifications, key=score_modification, reverse=True)
    
    def _approve_risky_modification(self, modification: FlowModification) -> bool:
        """Decide whether to approve a risky modification."""
        # In a real system, this might involve:
        # - Running extensive tests
        # - Getting human approval
        # - Checking system health metrics
        
        if modification.risk_level == "high":
            self.logger.warning(f"High-risk modification proposed: {modification.rationale}")
            # For now, we'll be conservative
            return False
        
        return True 