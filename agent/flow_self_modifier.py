"""
Flow Self-Modifier: Dynamic LLM Call Flow Management

This module implements a practical self-modifying system that can dynamically
adjust LLM call flows based on real-time performance and needs.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock
import inspect

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


@dataclass
class CallContext:
    """Context for an LLM call"""
    agent_type: str
    objective: str
    complexity_score: float = 0.5
    urgency: float = 0.5
    previous_failures: int = 0
    available_time: float = float('inf')
    available_budget: float = float('inf')


@dataclass
class CallDecision:
    """Decision about whether and how to make an LLM call"""
    should_call: bool
    use_cache: bool = False
    use_simplified_prompt: bool = False
    use_smaller_model: bool = False
    parallelize_with: List[str] = field(default_factory=list)
    defer_until: Optional[str] = None
    skip_reason: Optional[str] = None


class FlowSelfModifier:
    """
    A practical implementation of dynamic flow modification.
    Instead of modifying code, it makes real-time decisions about LLM calls.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.call_stats = defaultdict(lambda: {"calls": 0, "failures": 0, "total_time": 0})
        self.decision_cache = {}
        self.lock = Lock()
        
        # Configurable thresholds
        self.thresholds = {
            "max_calls_per_minute": 10,
            "max_sequential_calls": 3,
            "cache_similarity_threshold": 0.85,
            "simplification_threshold": 0.7,
            "parallel_opportunity_window": 5.0,  # seconds
        }
        
        # Track recent calls for pattern detection
        self.recent_calls = []
        self.call_window = 60  # seconds
        
    def should_make_call(self, context: CallContext) -> CallDecision:
        """
        Decide whether and how to make an LLM call based on current context.
        This is the main entry point for dynamic flow control.
        """
        self.logger.debug(f"FlowSelfModifier: Evaluating call for {context.agent_type}")
        
        # Clean old calls from history
        self._clean_old_calls()
        
        # Check rate limits
        if self._exceeds_rate_limit():
            return CallDecision(
                should_call=False,
                skip_reason="Rate limit exceeded"
            )
        
        # Check for caching opportunity
        cache_key = self._generate_cache_key(context)
        if cache_key in self.decision_cache:
            cached_decision = self.decision_cache[cache_key]
            if self._is_cache_valid(cached_decision):
                return CallDecision(
                    should_call=True,
                    use_cache=True
                )
        
        # Analyze current situation
        decision = self._analyze_and_decide(context)
        
        # Record this call
        self._record_call(context, decision)
        
        return decision
    
    def _analyze_and_decide(self, context: CallContext) -> CallDecision:
        """
        Analyze the context and make an intelligent decision about the call.
        """
        decision = CallDecision(should_call=True)
        
        # 1. Check if we can use a simpler approach
        if context.complexity_score < self.thresholds["simplification_threshold"]:
            decision.use_simplified_prompt = True
            decision.use_smaller_model = True
            self.logger.info(f"Using simplified approach for {context.agent_type}")
        
        # 2. Check for parallelization opportunities
        parallel_candidates = self._find_parallel_opportunities(context)
        if parallel_candidates:
            decision.parallelize_with = parallel_candidates
            self.logger.info(f"Can parallelize {context.agent_type} with {parallel_candidates}")
        
        # 3. Check if we should defer
        if context.urgency < 0.3 and self._has_higher_priority_pending():
            decision.should_call = False
            decision.defer_until = "next_cycle"
            self.logger.info(f"Deferring {context.agent_type} due to low urgency")
        
        # 4. Check failure patterns
        if context.previous_failures > 2:
            # Use meta-cognitive analysis for repeated failures
            meta_decision = self._get_meta_cognitive_decision(context)
            decision = self._apply_meta_decision(decision, meta_decision)
        
        return decision
    
    def _get_meta_cognitive_decision(self, context: CallContext) -> Dict[str, Any]:
        """
        Use LLM to make meta-cognitive decisions about difficult cases.
        """
        prompt = f"""
[META-COGNITIVE DECISION TASK]
An LLM call for {context.agent_type} has failed {context.previous_failures} times.

[CONTEXT]
- Objective: {context.objective}
- Complexity: {context.complexity_score:.2f}
- Urgency: {context.urgency:.2f}
- Recent call patterns: {self._get_recent_patterns()}

[DECISION NEEDED]
Should we:
1. Skip this call entirely?
2. Try a different approach?
3. Merge with another call?
4. Wait and retry later?

[OUTPUT FORMAT]
{{
  "decision": "skip|modify|merge|wait",
  "reasoning": "explanation",
  "alternative_approach": "description if modify",
  "merge_with": "agent_type if merge",
  "wait_duration": "seconds if wait"
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=prompt,
                temperature=0.3,
                logger=self.logger
            )
            
            if error:
                return {"decision": "skip", "reasoning": "Meta-cognitive call failed"}
            
            parsed, _ = parse_json_response(response, self.logger)
            return parsed or {"decision": "skip", "reasoning": "Failed to parse response"}
            
        except Exception as e:
            self.logger.error(f"Meta-cognitive decision failed: {e}")
            return {"decision": "skip", "reasoning": str(e)}
    
    def optimize_prompt(self, original_prompt: str, context: CallContext) -> str:
        """
        Dynamically optimize a prompt based on context.
        """
        if not context.use_simplified_prompt:
            return original_prompt
        
        # For now, simple truncation and focusing
        lines = original_prompt.split('\n')
        
        # Keep only essential sections
        essential_sections = ['[TASK]', '[OBJECTIVE]', '[OUTPUT', '[REQUIRED']
        filtered_lines = []
        keep_section = False
        
        for line in lines:
            if any(section in line.upper() for section in essential_sections):
                keep_section = True
            elif line.strip() == '' and keep_section:
                keep_section = False
            
            if keep_section or any(section in line.upper() for section in essential_sections):
                filtered_lines.append(line)
        
        simplified = '\n'.join(filtered_lines)
        
        # Add simplification instruction
        simplified += "\n\n[NOTE] Provide a concise, focused response."
        
        self.logger.debug(f"Simplified prompt from {len(original_prompt)} to {len(simplified)} chars")
        return simplified
    
    def select_model(self, default_model: str, context: CallContext) -> str:
        """
        Dynamically select the appropriate model based on context.
        """
        if context.use_smaller_model:
            # Map to smaller alternatives
            model_mapping = {
                "gpt-4": "gpt-3.5-turbo",
                "claude-2": "claude-instant",
                "gpt-3.5-turbo": "gpt-3.5-turbo",  # Already small
            }
            
            for full_model, small_model in model_mapping.items():
                if full_model in default_model:
                    self.logger.info(f"Downgrading from {default_model} to {small_model}")
                    return small_model
        
        return default_model
    
    def batch_calls(self, calls: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Batch multiple LLM calls into a single call when possible.
        """
        if len(calls) < 2:
            return None
        
        # Check if calls are batchable (similar types)
        agent_types = [call.get("context").agent_type for call in calls]
        if len(set(agent_types)) > 2:  # Too diverse
            return None
        
        # Create batched prompt
        batched_prompt = "[BATCHED LLM CALL]\nPlease handle multiple requests in one response:\n\n"
        
        for i, call in enumerate(calls):
            batched_prompt += f"--- REQUEST {i+1} ---\n"
            batched_prompt += call.get("prompt", "")
            batched_prompt += "\n\n"
        
        batched_prompt += "[OUTPUT FORMAT]\nProvide a JSON object with keys 'response_1', 'response_2', etc."
        
        return {
            "prompt": batched_prompt,
            "is_batched": True,
            "original_calls": calls
        }
    
    def _exceeds_rate_limit(self) -> bool:
        """Check if we're exceeding rate limits."""
        recent_count = len(self.recent_calls)
        return recent_count > self.thresholds["max_calls_per_minute"]
    
    def _find_parallel_opportunities(self, context: CallContext) -> List[str]:
        """Find calls that could be parallelized with this one."""
        opportunities = []
        
        # Look for calls in the near future that could be done together
        # This is simplified - in reality, we'd analyze the call graph
        parallel_candidates = {
            "architect": ["code_review"],
            "error_analysis": ["performance_analysis"],
            "maestro": []  # Maestro usually needs to run alone
        }
        
        return parallel_candidates.get(context.agent_type, [])
    
    def _has_higher_priority_pending(self) -> bool:
        """Check if there are higher priority calls pending."""
        # Simplified - in reality, we'd check the actual queue
        return False
    
    def _get_recent_patterns(self) -> Dict[str, Any]:
        """Analyze recent call patterns."""
        if not self.recent_calls:
            return {}
        
        patterns = {
            "total_calls": len(self.recent_calls),
            "calls_by_type": defaultdict(int),
            "average_complexity": 0,
            "failure_rate": 0
        }
        
        total_complexity = 0
        failures = 0
        
        for call in self.recent_calls:
            patterns["calls_by_type"][call["agent_type"]] += 1
            total_complexity += call.get("complexity", 0.5)
            if call.get("failed", False):
                failures += 1
        
        patterns["average_complexity"] = total_complexity / len(self.recent_calls)
        patterns["failure_rate"] = failures / len(self.recent_calls)
        
        return dict(patterns)
    
    def _apply_meta_decision(self, decision: CallDecision, 
                           meta_decision: Dict[str, Any]) -> CallDecision:
        """Apply meta-cognitive decision to the call decision."""
        meta_type = meta_decision.get("decision", "skip")
        
        if meta_type == "skip":
            decision.should_call = False
            decision.skip_reason = meta_decision.get("reasoning", "Meta-cognitive skip")
        elif meta_type == "wait":
            decision.should_call = False
            decision.defer_until = f"wait_{meta_decision.get('wait_duration', 60)}"
        elif meta_type == "modify":
            decision.use_simplified_prompt = True
            decision.use_smaller_model = True
        elif meta_type == "merge":
            merge_with = meta_decision.get("merge_with", "")
            if merge_with:
                decision.parallelize_with.append(merge_with)
        
        return decision
    
    def _generate_cache_key(self, context: CallContext) -> str:
        """Generate a cache key for the decision."""
        key_parts = [
            context.agent_type,
            str(hash(context.objective))[:8],
            f"c{int(context.complexity_score * 10)}",
            f"u{int(context.urgency * 10)}"
        ]
        return "_".join(key_parts)
    
    def _is_cache_valid(self, cached_decision: Dict[str, Any]) -> bool:
        """Check if a cached decision is still valid."""
        if "timestamp" not in cached_decision:
            return False
        
        age = time.time() - cached_decision["timestamp"]
        return age < 300  # 5 minutes
    
    def _record_call(self, context: CallContext, decision: CallDecision):
        """Record a call for pattern analysis."""
        with self.lock:
            self.recent_calls.append({
                "timestamp": time.time(),
                "agent_type": context.agent_type,
                "complexity": context.complexity_score,
                "decision": decision.should_call,
                "optimizations": {
                    "cache": decision.use_cache,
                    "simplified": decision.use_simplified_prompt,
                    "smaller_model": decision.use_smaller_model,
                    "parallel": bool(decision.parallelize_with)
                }
            })
            
            # Update stats
            stats = self.call_stats[context.agent_type]
            stats["calls"] += 1
    
    def _clean_old_calls(self):
        """Remove old calls from history."""
        cutoff = time.time() - self.call_window
        with self.lock:
            self.recent_calls = [
                call for call in self.recent_calls 
                if call["timestamp"] > cutoff
            ]
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get a report of optimization effectiveness."""
        report = {
            "total_calls": sum(stats["calls"] for stats in self.call_stats.values()),
            "calls_by_type": dict(self.call_stats),
            "optimization_stats": {
                "cache_uses": 0,
                "simplified_prompts": 0,
                "smaller_models": 0,
                "parallelized": 0,
                "skipped": 0
            },
            "patterns": self._get_recent_patterns()
        }
        
        # Count optimizations
        for call in self.recent_calls:
            opts = call.get("optimizations", {})
            if opts.get("cache"):
                report["optimization_stats"]["cache_uses"] += 1
            if opts.get("simplified"):
                report["optimization_stats"]["simplified_prompts"] += 1
            if opts.get("smaller_model"):
                report["optimization_stats"]["smaller_models"] += 1
            if opts.get("parallel"):
                report["optimization_stats"]["parallelized"] += 1
            if not call.get("decision"):
                report["optimization_stats"]["skipped"] += 1
        
        return report


# Global instance for easy access
_flow_modifier = None

def get_flow_modifier(model_config: Dict[str, str], logger: logging.Logger) -> FlowSelfModifier:
    """Get or create the global flow modifier instance."""
    global _flow_modifier
    if _flow_modifier is None:
        _flow_modifier = FlowSelfModifier(model_config, logger)
    return _flow_modifier


# Decorator for automatic flow optimization
def optimize_llm_call(agent_type: str):
    """
    Decorator to automatically optimize LLM calls.
    
    Usage:
        @optimize_llm_call("architect")
        def plan_action(self, objective, manifest):
            # ... function implementation
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract context from function arguments
            self = args[0] if args else None
            objective = args[1] if len(args) > 1 else kwargs.get("objective", "")
            
            # Get flow modifier
            if hasattr(self, "logger") and hasattr(self, "model_config"):
                flow_modifier = get_flow_modifier(self.model_config, self.logger)
                
                # Create context
                context = CallContext(
                    agent_type=agent_type,
                    objective=str(objective)[:100],  # Truncate for analysis
                    complexity_score=len(str(objective)) / 1000,  # Simple heuristic
                )
                
                # Get decision
                decision = flow_modifier.should_make_call(context)
                
                if not decision.should_call:
                    self.logger.info(f"Flow optimizer skipped call: {decision.skip_reason}")
                    return None, f"Skipped: {decision.skip_reason}"
                
                # Apply optimizations
                if decision.use_simplified_prompt:
                    self.logger.info("Using simplified prompt")
                    # Would need to modify the prompt in the function
                
                if decision.use_smaller_model:
                    self.logger.info("Using smaller model")
                    # Would need to modify model selection
            
            # Call original function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator 