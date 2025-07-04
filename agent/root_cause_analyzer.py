import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from enum import Enum

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response

class FailureType(Enum):
    """Types of failures the system can experience"""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    TIMEOUT = "timeout"
    API_FAILURE = "api_failure"
    VALIDATION_FAILURE = "validation_failure"
    INTEGRATION_FAILURE = "integration_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_FAILURE = "dependency_failure"
    UNKNOWN = "unknown"

class CausalLayer(Enum):
    """Different layers of causality"""
    IMMEDIATE = "immediate"      # Direct cause
    PROXIMATE = "proximate"     # Near cause
    SYSTEMIC = "systemic"       # System-level cause
    CULTURAL = "cultural"       # Process/methodology cause
    ENVIRONMENTAL = "environmental"  # External factors

@dataclass
class FailureEvent:
    """A single failure event with comprehensive metadata"""
    timestamp: datetime
    failure_type: FailureType
    agent_type: str
    objective: str
    error_message: str
    context: Dict[str, Any]
    severity: float  # 0.0 to 1.0
    impact_scope: List[str]  # What was affected
    recovery_time: Optional[float] = None
    resolution_strategy: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)

@dataclass
class CausalFactor:
    """A factor that contributes to failures"""
    factor_id: str
    description: str
    layer: CausalLayer
    confidence: float  # 0.0 to 1.0
    frequency: int  # How often this factor appears
    correlation_strength: float  # Correlation with failures
    mitigation_strategies: List[str] = field(default_factory=list)

@dataclass
class RootCauseAnalysis:
    """Complete root cause analysis result"""
    analysis_id: str
    timestamp: datetime
    analyzed_failures: List[FailureEvent]
    causal_chain: List[CausalFactor]
    primary_root_causes: List[str]
    contributing_factors: List[str]
    systemic_issues: List[str]
    recommended_actions: List[Dict[str, Any]]
    confidence_score: float
    analysis_depth: str  # "surface", "intermediate", "deep"

class RootCauseAnalyzer:
    """
    Advanced root cause analysis system that can identify deep, systemic
    issues and provide actionable recommendations for improvement.
    """

    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        
        # Failure tracking
        self.failure_history = []
        self.causal_factors_db = {}
        self.pattern_library = {}
        
        # Analysis configuration
        self.analysis_depth_levels = {
            "surface": {"lookback_days": 7, "min_failures": 3},
            "intermediate": {"lookback_days": 30, "min_failures": 10},
            "deep": {"lookback_days": 90, "min_failures": 20}
        }
        
        # Known patterns and signatures
        self.failure_signatures = {}
        self.causal_relationships = defaultdict(list)
        
        # Learning from analysis results
        self.analysis_history = []
        self.successful_mitigations = {}
        
        self.logger.info("🔍 RootCauseAnalyzer initialized - Ready for deep analysis!")

    def record_failure(self, agent_type: str, objective: str, error_message: str,
                      failure_type: FailureType, context: Optional[Dict[str, Any]] = None,
                      severity: float = 0.5, impact_scope: Optional[List[str]] = None) -> str:
        """
        Record a failure event for later analysis.
        """
        failure_event = FailureEvent(
            timestamp=datetime.now(),
            failure_type=failure_type,
            agent_type=agent_type,
            objective=objective,
            error_message=error_message,
            context=context or {},
            severity=severity,
            impact_scope=impact_scope or [agent_type]
        )
        
        self.failure_history.append(failure_event)
        
        # Trigger analysis if we have enough recent failures
        recent_failures = self._get_recent_failures(hours=1)
        if len(recent_failures) >= 3:  # Threshold for immediate analysis
            self.logger.warning("🚨 Multiple recent failures detected - triggering immediate analysis")
            self.analyze_failure_patterns("surface")
        
        failure_id = f"failure_{len(self.failure_history)}"
        self.logger.info(f"📝 Failure recorded: {failure_id} ({failure_type.value} in {agent_type})")
        return failure_id

    def analyze_failure_patterns(self, depth: str = "intermediate") -> RootCauseAnalysis:
        """
        Perform comprehensive root cause analysis of failure patterns.
        """
        self.logger.info(f"🔬 Starting {depth} root cause analysis...")
        
        analysis_config = self.analysis_depth_levels.get(depth, self.analysis_depth_levels["intermediate"])
        
        # Get failures for analysis
        cutoff_date = datetime.now() - timedelta(days=analysis_config["lookback_days"])
        relevant_failures = [f for f in self.failure_history if f.timestamp >= cutoff_date]
        
        if len(relevant_failures) < analysis_config["min_failures"]:
            self.logger.warning(f"Insufficient failures for {depth} analysis: {len(relevant_failures)}")
            return self._create_minimal_analysis(relevant_failures, depth)
        
        # Multi-layered analysis
        causal_chain = self._analyze_causal_chain(relevant_failures)
        primary_root_causes = self._identify_primary_root_causes(relevant_failures, causal_chain)
        systemic_issues = self._identify_systemic_issues(relevant_failures, causal_chain)
        
        # Generate recommendations
        recommendations = self._generate_action_recommendations(
            relevant_failures, primary_root_causes, systemic_issues
        )
        
        # Calculate confidence
        confidence_score = self._calculate_analysis_confidence(
            relevant_failures, causal_chain, primary_root_causes
        )
        
        # Create analysis result
        analysis = RootCauseAnalysis(
            analysis_id=f"rca_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            analyzed_failures=relevant_failures,
            causal_chain=causal_chain,
            primary_root_causes=primary_root_causes,
            contributing_factors=self._extract_contributing_factors(causal_chain),
            systemic_issues=systemic_issues,
            recommended_actions=recommendations,
            confidence_score=confidence_score,
            analysis_depth=depth
        )
        
        # Store analysis for learning
        self.analysis_history.append(analysis)
        
        # Log key findings
        self._log_analysis_results(analysis)
        
        return analysis

    def _analyze_causal_chain(self, failures: List[FailureEvent]) -> List[CausalFactor]:
        """
        Analyze the causal chain leading to failures using AI-powered analysis.
        """
        self.logger.info("🔗 Analyzing causal chain...")
        
        # Prepare failure summary for AI analysis
        failure_summary = self._prepare_failure_summary(failures)
        
        causal_analysis_prompt = f"""
[ROOT CAUSE ANALYSIS TASK]
Analyze these failure patterns to identify the causal chain.

[FAILURE SUMMARY]
{failure_summary}

[ANALYSIS FRAMEWORK]
Use the "5 Whys" methodology and systems thinking to identify:
1. Immediate causes (what directly caused the failure)
2. Proximate causes (what led to the immediate cause)
3. Systemic causes (system-level issues)
4. Cultural causes (process/methodology issues)
5. Environmental causes (external factors)

[OUTPUT FORMAT]
{{
  "causal_factors": [
    {{
      "factor_id": "unique_identifier",
      "description": "detailed description",
      "layer": "immediate|proximate|systemic|cultural|environmental",
      "confidence": 0.8,
      "evidence": ["supporting evidence"],
      "frequency_indicator": "how often this appears",
      "mitigation_strategies": ["potential solutions"]
    }}
  ],
  "causal_relationships": [
    {{
      "cause": "factor_id",
      "effect": "factor_id",
      "strength": 0.9
    }}
  ]
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=causal_analysis_prompt,
                temperature=0.3,
                logger=self.logger
            )
            
            if error or not response:
                return self._fallback_causal_analysis(failures)
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return self._fallback_causal_analysis(failures)
            
            # Convert to CausalFactor objects
            causal_factors = []
            for factor_data in parsed.get("causal_factors", []):
                factor = CausalFactor(
                    factor_id=factor_data["factor_id"],
                    description=factor_data["description"],
                    layer=CausalLayer(factor_data["layer"]),
                    confidence=factor_data["confidence"],
                    frequency=self._calculate_factor_frequency(factor_data, failures),
                    correlation_strength=0.8,  # Will be calculated later
                    mitigation_strategies=factor_data.get("mitigation_strategies", [])
                )
                causal_factors.append(factor)
            
            # Store causal relationships
            for rel in parsed.get("causal_relationships", []):
                self.causal_relationships[rel["cause"]].append({
                    "effect": rel["effect"],
                    "strength": rel["strength"]
                })
            
            return causal_factors
            
        except Exception as e:
            self.logger.error(f"Causal chain analysis failed: {e}")
            return self._fallback_causal_analysis(failures)

    def _prepare_failure_summary(self, failures: List[FailureEvent]) -> str:
        """Prepare a concise summary of failures for AI analysis."""
        summary_parts = []
        
        # Overall statistics
        total_failures = len(failures)
        failure_types = Counter(f.failure_type.value for f in failures)
        agent_types = Counter(f.agent_type for f in failures)
        severity_avg = statistics.mean(f.severity for f in failures)
        
        summary_parts.append(f"Total Failures: {total_failures}")
        summary_parts.append(f"Average Severity: {severity_avg:.2f}")
        summary_parts.append(f"Failure Types: {dict(failure_types)}")
        summary_parts.append(f"Affected Agents: {dict(agent_types)}")
        
        # Recent failure examples
        summary_parts.append("\nRecent Failure Examples:")
        for i, failure in enumerate(failures[-5:]):  # Last 5 failures
            summary_parts.append(f"{i+1}. {failure.agent_type}: {failure.error_message[:100]}...")
        
        # Temporal patterns
        time_patterns = self._analyze_temporal_patterns(failures)
        if time_patterns:
            summary_parts.append(f"\nTemporal Patterns: {time_patterns}")
        
        return "\n".join(summary_parts)

    def _identify_primary_root_causes(self, failures: List[FailureEvent],
                                    causal_chain: List[CausalFactor]) -> List[str]:
        """
        Identify the primary root causes from the causal chain.
        """
        # Find systemic and cultural layer factors with high confidence
        root_causes = []
        
        for factor in causal_chain:
            if (factor.layer in [CausalLayer.SYSTEMIC, CausalLayer.CULTURAL] and
                factor.confidence > 0.7 and
                factor.frequency > len(failures) * 0.3):  # Appears in >30% of cases
                root_causes.append(factor.description)
        
        # If no clear systemic causes, look at high-frequency proximate causes
        if not root_causes:
            proximate_causes = [f for f in causal_chain if f.layer == CausalLayer.PROXIMATE]
            proximate_causes.sort(key=lambda x: x.frequency * x.confidence, reverse=True)
            root_causes = [f.description for f in proximate_causes[:3]]
        
        return root_causes

    def _identify_systemic_issues(self, failures: List[FailureEvent],
                                causal_chain: List[CausalFactor]) -> List[str]:
        """
        Identify broader systemic issues affecting the system.
        """
        systemic_issues = []
        
        # Cross-agent failures indicate systemic issues
        affected_agents = set(f.agent_type for f in failures)
        if len(affected_agents) > 2:
            systemic_issues.append("Cross-agent failure pattern indicates systemic architectural issues")
        
        # High-frequency failure types
        failure_type_counts = Counter(f.failure_type for f in failures)
        for failure_type, count in failure_type_counts.items():
            if count > len(failures) * 0.4:  # >40% of failures
                systemic_issues.append(f"High frequency of {failure_type.value} suggests systemic weakness")
        
        # Escalating severity
        if len(failures) >= 5:
            recent_severity = statistics.mean(f.severity for f in failures[-5:])
            earlier_severity = statistics.mean(f.severity for f in failures[:-5])
            if recent_severity > earlier_severity + 0.2:
                systemic_issues.append("Escalating failure severity indicates degrading system health")
        
        # Time-based patterns
        temporal_issues = self._analyze_systemic_temporal_issues(failures)
        systemic_issues.extend(temporal_issues)
        
        return systemic_issues

    def _generate_action_recommendations(self, failures: List[FailureEvent],
                                       root_causes: List[str],
                                       systemic_issues: List[str]) -> List[Dict[str, Any]]:
        """
        Generate specific, actionable recommendations based on the analysis.
        """
        recommendation_prompt = f"""
[ACTION RECOMMENDATION GENERATION]
Based on this root cause analysis, generate specific, actionable recommendations.

[ROOT CAUSES]
{json.dumps(root_causes, indent=2)}

[SYSTEMIC ISSUES]
{json.dumps(systemic_issues, indent=2)}

[FAILURE CONTEXT]
- Total failures analyzed: {len(failures)}
- Most common failure type: {Counter(f.failure_type.value for f in failures).most_common(1)[0] if failures else 'None'}
- Most affected agent: {Counter(f.agent_type for f in failures).most_common(1)[0] if failures else 'None'}

[RECOMMENDATION REQUIREMENTS]
1. Address root causes, not just symptoms
2. Prioritize by impact and feasibility
3. Include both immediate and long-term actions
4. Specify success metrics for each recommendation

[OUTPUT FORMAT]
{{
  "recommendations": [
    {{
      "id": "rec_001",
      "title": "Short descriptive title",
      "description": "Detailed action description",
      "priority": "high|medium|low",
      "timeframe": "immediate|short_term|long_term",
      "effort_estimate": "low|medium|high",
      "expected_impact": "description of expected impact",
      "success_metrics": ["measurable success criteria"],
      "implementation_steps": ["step 1", "step 2", "..."],
      "risk_factors": ["potential risks or challenges"]
    }}
  ]
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=recommendation_prompt,
                temperature=0.4,
                logger=self.logger
            )
            
            if error or not response:
                return self._fallback_recommendations(root_causes, systemic_issues)
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return self._fallback_recommendations(root_causes, systemic_issues)
            
            return parsed.get("recommendations", [])
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return self._fallback_recommendations(root_causes, systemic_issues)

    def _fallback_causal_analysis(self, failures: List[FailureEvent]) -> List[CausalFactor]:
        """Fallback causal analysis using heuristics."""
        factors = []
        
        # Analyze error message patterns
        error_patterns = Counter(f.error_message.split()[0] if f.error_message else "unknown"
                               for f in failures)
        
        for pattern, frequency in error_patterns.most_common(3):
            factors.append(CausalFactor(
                factor_id=f"pattern_{pattern}",
                description=f"High frequency of errors starting with '{pattern}'",
                layer=CausalLayer.IMMEDIATE,
                confidence=0.6,
                frequency=frequency,
                correlation_strength=frequency / len(failures)
            ))
        
        return factors

    def _fallback_recommendations(self, root_causes: List[str],
                                systemic_issues: List[str]) -> List[Dict[str, Any]]:
        """Generate fallback recommendations."""
        recommendations = []
        
        if root_causes:
            recommendations.append({
                "id": "rec_001",
                "title": "Address Primary Root Causes",
                "description": f"Focus on resolving: {', '.join(root_causes[:2])}",
                "priority": "high",
                "timeframe": "short_term",
                "effort_estimate": "medium",
                "expected_impact": "Significant reduction in failure frequency",
                "success_metrics": ["Reduce failure rate by 50%"],
                "implementation_steps": ["Analyze specific causes", "Implement fixes", "Monitor results"]
            })
        
        if systemic_issues:
            recommendations.append({
                "id": "rec_002",
                "title": "Address Systemic Issues",
                "description": f"Resolve system-wide problems: {', '.join(systemic_issues[:2])}",
                "priority": "medium",
                "timeframe": "long_term",
                "effort_estimate": "high",
                "expected_impact": "Improved overall system stability",
                "success_metrics": ["Reduce cross-agent failures by 40%"],
                "implementation_steps": ["Architecture review", "System redesign", "Gradual implementation"]
            })
        
        return recommendations

    def _calculate_analysis_confidence(self, failures: List[FailureEvent],
                                     causal_chain: List[CausalFactor],
                                     root_causes: List[str]) -> float:
        """Calculate confidence score for the analysis."""
        factors = []
        
        # Data quality factor
        data_quality = min(1.0, len(failures) / 20)  # More data = higher confidence
        factors.append(data_quality * 0.3)
        
        # Causal chain completeness
        chain_completeness = len(causal_chain) / 10  # Assume 10 is comprehensive
        factors.append(min(1.0, chain_completeness) * 0.2)
        
        # Root cause clarity
        root_cause_clarity = 1.0 if root_causes else 0.3
        factors.append(root_cause_clarity * 0.3)
        
        # Pattern consistency
        pattern_consistency = self._calculate_pattern_consistency(failures)
        factors.append(pattern_consistency * 0.2)
        
        return sum(factors)

    def _calculate_pattern_consistency(self, failures: List[FailureEvent]) -> float:
        """Calculate how consistent failure patterns are."""
        if len(failures) < 2:
            return 0.5
        
        # Check consistency in failure types
        failure_types = [f.failure_type for f in failures]
        most_common_type = Counter(failure_types).most_common(1)[0][1]
        type_consistency = most_common_type / len(failures)
        
        # Check consistency in agent types
        agent_types = [f.agent_type for f in failures]
        most_common_agent = Counter(agent_types).most_common(1)[0][1]
        agent_consistency = most_common_agent / len(failures)
        
        return (type_consistency + agent_consistency) / 2

    def _get_recent_failures(self, hours: int = 24) -> List[FailureEvent]:
        """Get failures from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [f for f in self.failure_history if f.timestamp >= cutoff]

    def _analyze_temporal_patterns(self, failures: List[FailureEvent]) -> Dict[str, Any]:
        """Analyze temporal patterns in failures."""
        if len(failures) < 3:
            return {}
        
        # Time clustering
        timestamps = [f.timestamp for f in failures]
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds()
                     for i in range(len(timestamps)-1)]
        
        avg_interval = statistics.mean(time_diffs)
        
        patterns = {}
        if avg_interval < 300:  # 5 minutes
            patterns["burst_pattern"] = "Failures occurring in rapid bursts"
        elif avg_interval < 3600:  # 1 hour
            patterns["frequent_pattern"] = "High frequency failure pattern"
        
        return patterns

    def _analyze_systemic_temporal_issues(self, failures: List[FailureEvent]) -> List[str]:
        """Analyze systemic issues related to timing."""
        issues = []
        
        if len(failures) < 5:
            return issues
        
        # Check for acceleration
        recent_failures = failures[-5:]
        earlier_failures = failures[:-5] if len(failures) > 5 else []
        
        if earlier_failures:
            recent_rate = len(recent_failures) / 5
            earlier_rate = len(earlier_failures) / max(1, len(earlier_failures))
            
            if recent_rate > earlier_rate * 2:
                issues.append("Failure rate is accelerating - indicates system degradation")
        
        # Check for cascading failures
        timestamps = [f.timestamp for f in failures[-10:]]  # Last 10 failures
        for i in range(len(timestamps) - 2):
            time_diff1 = (timestamps[i+1] - timestamps[i]).total_seconds()
            time_diff2 = (timestamps[i+2] - timestamps[i+1]).total_seconds()
            
            if time_diff1 < 60 and time_diff2 < 60:  # Within 1 minute each
                issues.append("Cascading failure pattern detected - indicates poor error isolation")
                break
        
        return issues

    def _calculate_factor_frequency(self, factor_data: Dict[str, Any],
                                  failures: List[FailureEvent]) -> int:
        """Calculate how frequently a causal factor appears."""
        # Simple heuristic - in practice would be more sophisticated
        factor_keywords = factor_data["description"].lower().split()
        
        frequency = 0
        for failure in failures:
            failure_text = (failure.error_message + " " + failure.objective).lower()
            if any(keyword in failure_text for keyword in factor_keywords):
                frequency += 1
        
        return frequency

    def _extract_contributing_factors(self, causal_chain: List[CausalFactor]) -> List[str]:
        """Extract contributing factors from causal chain."""
        contributing = []
        
        for factor in causal_chain:
            if factor.layer in [CausalLayer.PROXIMATE, CausalLayer.ENVIRONMENTAL]:
                contributing.append(factor.description)
        
        return contributing

    def _create_minimal_analysis(self, failures: List[FailureEvent],
                               depth: str) -> RootCauseAnalysis:
        """Create minimal analysis when insufficient data."""
        return RootCauseAnalysis(
            analysis_id=f"minimal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            analyzed_failures=failures,
            causal_chain=[],
            primary_root_causes=["Insufficient data for analysis"],
            contributing_factors=[],
            systemic_issues=[],
            recommended_actions=[{
                "id": "rec_001",
                "title": "Collect More Data",
                "description": "Need more failure data for meaningful analysis",
                "priority": "medium",
                "timeframe": "ongoing",
                "effort_estimate": "low"
            }],
            confidence_score=0.1,
            analysis_depth=depth
        )

    def _log_analysis_results(self, analysis: RootCauseAnalysis):
        """Log key findings from the analysis."""
        self.logger.info(f"🔬 Root Cause Analysis Complete: {analysis.analysis_id}")
        self.logger.info(f"📊 Analyzed {len(analysis.analyzed_failures)} failures")
        self.logger.info(f"🎯 Confidence Score: {analysis.confidence_score:.3f}")
        
        if analysis.primary_root_causes:
            self.logger.info("🔍 Primary Root Causes:")
            for cause in analysis.primary_root_causes:
                self.logger.info(f"  • {cause}")
        
        if analysis.systemic_issues:
            self.logger.info("⚠️ Systemic Issues:")
            for issue in analysis.systemic_issues:
                self.logger.info(f"  • {issue}")
        
        self.logger.info(f"💡 Generated {len(analysis.recommended_actions)} recommendations")

    def get_analysis_report(self) -> Dict[str, Any]:
        """Get comprehensive analysis report."""
        recent_analyses = self.analysis_history[-5:]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_failures_recorded": len(self.failure_history),
            "analyses_performed": len(self.analysis_history),
            "recent_analyses": [
                {
                    "id": a.analysis_id,
                    "timestamp": a.timestamp.isoformat(),
                    "confidence": a.confidence_score,
                    "failures_analyzed": len(a.analyzed_failures),
                    "root_causes_found": len(a.primary_root_causes)
                }
                for a in recent_analyses
            ],
            "failure_statistics": self._get_failure_statistics(),
            "top_root_causes": self._get_top_root_causes(),
            "improvement_trends": self._calculate_improvement_trends()
        }

    def _get_failure_statistics(self) -> Dict[str, Any]:
        """Get failure statistics."""
        if not self.failure_history:
            return {}
        
        recent_failures = self._get_recent_failures(hours=168)  # Last week
        
        return {
            "total_failures": len(self.failure_history),
            "recent_failures": len(recent_failures),
            "failure_types": dict(Counter(f.failure_type.value for f in recent_failures)),
            "agent_types": dict(Counter(f.agent_type for f in recent_failures)),
            "average_severity": statistics.mean(f.severity for f in recent_failures) if recent_failures else 0
        }

    def _get_top_root_causes(self) -> List[Dict[str, Any]]:
        """Get most common root causes from analysis history."""
        all_causes = []
        for analysis in self.analysis_history:
            all_causes.extend(analysis.primary_root_causes)
        
        cause_counts = Counter(all_causes)
        return [{"cause": cause, "frequency": count}
                for cause, count in cause_counts.most_common(5)]

    def _calculate_improvement_trends(self) -> Dict[str, Any]:
        """Calculate if things are improving over time."""
        if len(self.analysis_history) < 2:
            return {"trend": "insufficient_data"}
        
        # Compare recent vs earlier analysis confidence
        recent_avg = statistics.mean(a.confidence_score for a in self.analysis_history[-3:])
        earlier_avg = statistics.mean(a.confidence_score for a in self.analysis_history[:-3])
        
        trend = "improving" if recent_avg > earlier_avg else "declining"
        
        return {
            "trend": trend,
            "recent_confidence": recent_avg,
            "earlier_confidence": earlier_avg,
            "confidence_change": recent_avg - earlier_avg
        }

# Global instance
_root_cause_analyzer = None

def get_root_cause_analyzer(model_config: Dict[str, str], logger: logging.Logger) -> RootCauseAnalyzer:
    """Get or create the global root cause analyzer instance."""
    global _root_cause_analyzer
    if _root_cause_analyzer is None:
        _root_cause_analyzer = RootCauseAnalyzer(model_config, logger)
    return _root_cause_analyzer