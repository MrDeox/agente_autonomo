import json
import datetime
import os
import re
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import timezone # Adicionado
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import logging


@dataclass
class SemanticPattern:
    """Represents a learned pattern in objectives or strategies."""
    pattern_id: str
    pattern_type: str  # "objective_pattern", "failure_pattern", "success_pattern"
    pattern_keywords: List[str]
    success_rate: float
    frequency: int
    confidence: float
    first_seen: str
    last_seen: str
    examples: List[str]


@dataclass
class Heuristic:
    """Represents a learned heuristic about what works and what doesn't."""
    heuristic_id: str
    rule_type: str  # "avoid", "prefer", "sequence", "context"
    condition: str
    action: str
    success_rate: float
    confidence: float
    evidence_count: int
    created_date: str
    last_applied: Optional[str] = None


@dataclass
class SemanticCluster:
    """Groups similar objectives/strategies for pattern recognition."""
    cluster_id: str
    cluster_type: str
    keywords: List[str]
    members: List[str]  # objective/strategy IDs
    centroid_embedding: Optional[List[float]]
    success_rate: float
    created_date: str


class Memory:
    """
    Manages persistent memory for the Hephaestus agent, storing historical data
    about objectives, failures, and acquired capabilities.
    """
    def __init__(self, filepath: str = "HEPHAESTUS_MEMORY.json", max_objectives_history: int = 20, logger: Optional[logging.Logger] = None):
        """
        Initializes the Memory module.

        Args:
            filepath: The path to the JSON file used for storing memory.
            max_objectives_history: The maximum number of objectives to keep in history.
            logger: The logger instance.
        """
        self.filepath: str = filepath
        self.max_objectives_history: int = max_objectives_history
        self.logger = logger or logging.getLogger(__name__) # Use provided logger or create a new one
        self.completed_objectives: List[Dict[str, Any]] = []
        self.failed_objectives: List[Dict[str, Any]] = []
        self.acquired_capabilities: List[Dict[str, Any]] = []
        self.recent_objectives_log: List[Dict[str, Any]] = [] # Novo atributo
        self.cycle_count: int = 0
        
        # Advanced memory features
        self.semantic_patterns: Dict[str, SemanticPattern] = {}
        self.learned_heuristics: Dict[str, Heuristic] = {}
        self.semantic_clusters: Dict[str, SemanticCluster] = {}
        self.pattern_recognition_enabled: bool = True
        self.min_pattern_frequency: int = 3
        self.min_confidence_threshold: float = 0.7

    def _get_timestamp(self) -> str:
        """Returns a standardized ISO format timestamp."""
        return datetime.datetime.now(timezone.utc).isoformat()

    def load(self) -> None:
        """
        Loads memory data from the specified JSON file.
        If the file doesn't exist, it starts with an empty memory.
        """
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_objectives = data.get("completed_objectives", [])
                    self.failed_objectives = data.get("failed_objectives", [])
                    self.acquired_capabilities = data.get("acquired_capabilities", [])
                    self.recent_objectives_log = data.get("recent_objectives_log", []) # Carregar novo atributo
                    
                    # Load advanced memory features
                    patterns_data = data.get("semantic_patterns", {})
                    self.semantic_patterns = {k: SemanticPattern(**v) for k, v in patterns_data.items()}
                    
                    heuristics_data = data.get("learned_heuristics", {})
                    self.learned_heuristics = {k: Heuristic(**v) for k, v in heuristics_data.items()}
                    
                    clusters_data = data.get("semantic_clusters", {})
                    self.semantic_clusters = {k: SemanticCluster(**v) for k, v in clusters_data.items()}
            else:
                # File not found, start with empty memory (already initialized)
                pass
        except FileNotFoundError:
            # Should be caught by os.path.exists, but as a safeguard
            pass # Start with empty memory
        except json.JSONDecodeError:
            # File is corrupted or not valid JSON, start with empty memory
            # Optionally, log this event
            print(f"Warning: Memory file {self.filepath} is corrupted or not valid JSON. Starting with empty memory.")
            self.completed_objectives = []
            self.failed_objectives = []
            self.acquired_capabilities = []
            self.recent_objectives_log = []
        except Exception as e:
            # Other potential errors during loading
            print(f"Error loading memory from {self.filepath}: {e}. Starting with empty memory.")
            self.completed_objectives = []
            self.failed_objectives = []
            self.acquired_capabilities = []
            self.recent_objectives_log = []


    def save(self) -> None:
        """
        Saves the current memory state to the JSON file.
        """
        data = {
            "completed_objectives": self.completed_objectives,
            "failed_objectives": self.failed_objectives,
            "acquired_capabilities": self.acquired_capabilities,
            "recent_objectives_log": self.recent_objectives_log, # Salvar novo atributo
            
            # Save advanced memory features
            "semantic_patterns": {k: asdict(v) for k, v in self.semantic_patterns.items()},
            "learned_heuristics": {k: asdict(v) for k, v in self.learned_heuristics.items()},
            "semantic_clusters": {k: asdict(v) for k, v in self.semantic_clusters.items()}
        }
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            # Handle potential IO errors during save (e.g., disk full, permissions)
            print(f"Error saving memory to {self.filepath}: {e}")


    def add_completed_objective(self, objective: str, strategy: str, details: str) -> None:
        """
        Adds a record of a successfully completed objective.

        Args:
            objective: The description of the objective.
            strategy: The strategy used to achieve the objective.
            details: Any relevant details or context about the completion.
        """
        record = {
            "objective": objective,
            "strategy_used": strategy,
            "details": details,
            "date": self._get_timestamp(),
            "status": "completed"  # Adicionado status
        }
        self.completed_objectives.append(record)
        self._add_to_recent_objectives_log(objective, "success")

    def _add_to_recent_objectives_log(self, objective: str, status: str, reason: Optional[str] = None) -> None:
        """Helper method to add to the recent objectives log and keep it trimmed."""
        log_entry = {
            "objective": objective,
            "status": status,
            "reason": reason, # Can be None for successes
            "date": self._get_timestamp()
        }
        self.recent_objectives_log.append(log_entry)
        # Keep only the last 5 entries
        if len(self.recent_objectives_log) > 5:
            self.recent_objectives_log = self.recent_objectives_log[-5:]
        self.cleanup_memory() # Call cleanup_memory after each objective addition

    def cleanup_memory(self) -> None:
        """
        Cleans up memory by removing old, duplicate, or abandoned objectives
        if the cycle count reaches 5.
        """
        self.cycle_count += 1
        if self.cycle_count < 5:
            return

        self.cycle_count = 0  # Reset cycle count

        # 1. Combine all historical objectives
        all_historical_objectives = self.completed_objectives + self.failed_objectives

        # 2. Sort by date (older to newer) to ensure the latest is kept during deduplication
        all_historical_objectives.sort(key=lambda x: x["date"])

        # 3. Deduplicate by 'objective' string, keeping the most recent entry (due to prior sort)
        unique_objectives_dict: Dict[str, Dict[str, Any]] = {}
        for obj in all_historical_objectives:
            unique_objectives_dict[obj["objective"]] = obj # Keeps the last one encountered for a given key

        # 4. Convert back to list, now containing unique objectives (most recent version of each)
        # Sort by date (most recent first) for truncation
        unique_objectives_list = sorted(
            list(unique_objectives_dict.values()),
            key=lambda x: x["date"],
            reverse=True
        )

        # 5. Truncate to max_objectives_history
        kept_objectives = unique_objectives_list[:self.max_objectives_history]

        # 6. Clear and reconstruct completed_objectives and failed_objectives lists
        self.completed_objectives = []
        self.failed_objectives = []

        for obj in kept_objectives:
            # obj now contains the "status" field added in add_completed/failed_objective
            if obj.get("status") == "completed": # Use .get() for safety, though status should exist
                self.completed_objectives.append(obj)
            elif obj.get("status") == "failed":
                self.failed_objectives.append(obj)
            # else: could log an error if status is missing or unexpected

        # 7. Re-sort the separated lists chronologically (older to newer)
        # This maintains the original order for items within their respective lists.
        self.completed_objectives.sort(key=lambda x: x["date"])
        self.failed_objectives.sort(key=lambda x: x["date"])


    def add_failed_objective(self, objective: str, reason: str, details: str) -> None:
        """
        Adds a record of a failed objective.

        Args:
            objective: The description of the objective.
            reason: The primary reason for the failure.
            details: Any relevant details or context about the failure.
        """
        record = {
            "objective": objective,
            "reason": reason,
            "details": details,
            "date": self._get_timestamp(),
            "status": "failed"  # Adicionado status
        }
        self.failed_objectives.append(record)
        self._add_to_recent_objectives_log(objective, "failure", reason=reason)

    def add_capability(self, capability_description: str, related_objective: Optional[str] = None) -> None:
        """
        Adds a record of a newly acquired capability.

        Args:
            capability_description: A description of the new capability.
            related_objective: Optional. The objective that led to this capability.
        """
        record = {
            "description": capability_description,
            "related_objective": related_objective,
            "date": self._get_timestamp()
        }
        self.acquired_capabilities.append(record)

    def get_history_summary(self, max_items_per_category: int = 3) -> str:
        """
        Generates a concise text summary of recent activities.

        Args:
            max_items_per_category: Max number of items from completed and failed objectives to include.

        Returns:
            A string summarizing recent history.
        """
        summary_parts = []

        if self.completed_objectives:
            summary_parts.append("Recent Successes:")
            for item in reversed(self.completed_objectives[-max_items_per_category:]):
                summary_parts.append(f"  - Objective: \"{item['objective'][:100]}...\" (Strategy: {item['strategy_used']}, Date: {item['date']})")

        if self.failed_objectives:
            summary_parts.append("\nRecent Failures:")
            for item in reversed(self.failed_objectives[-max_items_per_category:]):
                summary_parts.append(f"  - Objective: \"{item['objective'][:100]}...\" (Reason: {item['reason']}, Date: {item['date']})")

        if self.acquired_capabilities:
            summary_parts.append("\nRecent Capabilities Acquired:")
            for item in reversed(self.acquired_capabilities[-max_items_per_category:]):
                summary_parts.append(f"  - Capability: \"{item['description'][:100]}...\" (Date: {item['date']})")

        if not summary_parts:
            return "No significant history recorded yet."

        return "\n".join(summary_parts)

    def get_full_history_for_prompt(self, max_completed: int = 2, max_failed: int = 2, max_capabilities: int = 1) -> str:
        """
        Generates a more detailed, but still concise, history string formatted for an LLM prompt.
        Prioritizes the most recent items.
        """
        prompt_lines = []

        if self.completed_objectives:
            prompt_lines.append("Completed Objectives (most recent first):")
            for record in reversed(self.completed_objectives[-max_completed:]):
                prompt_lines.append(
                    f"- Objective: {record['objective']}\n  Strategy: {record['strategy_used']}\n  Outcome: {record['details'][:150]}...\n  Date: {record['date']}"
                )
            prompt_lines.append("") # Add a blank line for separation

        if self.failed_objectives:
            prompt_lines.append("Failed Objectives (most recent first):")
            for record in reversed(self.failed_objectives[-max_failed:]):
                prompt_lines.append(
                    f"- Objective: {record['objective']}\n  Reason: {record['reason']}\n  Details: {record['details'][:150]}...\n  Date: {record['date']}"
                )
            prompt_lines.append("")

        if self.acquired_capabilities:
            prompt_lines.append("Acquired Capabilities (most recent first):")
            for record in reversed(self.acquired_capabilities[-max_capabilities:]):
                prompt_lines.append(
                    f"- Capability: {record['description']}\n  Related to: {record.get('related_objective', 'N/A')}\n  Date: {record['date']}"
                )
            prompt_lines.append("")

        if not prompt_lines:
            return "No relevant history available."

        return "\n".join(prompt_lines).strip()
    
    def has_degenerative_failure_pattern(self, objective: str, reason: str, threshold: int = 2) -> bool:
        """
        Checks if a specific objective has failed repeatedly for the same reason.

        Args:
            objective: The objective to check.
            reason: The failure reason to check for.
            threshold: The number of failures to be considered a degenerative pattern.

        Returns:
            True if the pattern is detected, False otherwise.
        """
        count = 0
        for log_entry in reversed(self.recent_objectives_log):
            if log_entry.get("objective") == objective and log_entry.get("status") == "failure" and log_entry.get("reason") == reason:
                count += 1
        
        if count >= threshold:
            self.logger.warning(
                f"Degenerative failure pattern detected for objective '{objective}' with reason '{reason}'. Count: {count}"
            )
            return True
            
        return False

    # Advanced Memory Methods
    
    def analyze_semantic_patterns(self) -> Dict[str, Any]:
        """
        Analyze objectives and outcomes to identify semantic patterns.
        """
        if not self.pattern_recognition_enabled:
            return {"patterns_analyzed": 0, "new_patterns": 0}
        
        patterns_found = 0
        new_patterns = 0
        
        # Analyze success patterns
        success_patterns = self._identify_success_patterns()
        for pattern in success_patterns:
            patterns_found += 1
            if pattern.pattern_id not in self.semantic_patterns:
                new_patterns += 1
                self.semantic_patterns[pattern.pattern_id] = pattern
        
        # Analyze failure patterns
        failure_patterns = self._identify_failure_patterns()
        for pattern in failure_patterns:
            patterns_found += 1
            if pattern.pattern_id not in self.semantic_patterns:
                new_patterns += 1
                self.semantic_patterns[pattern.pattern_id] = pattern
        
        # Update existing patterns
        self._update_pattern_statistics()
        
        return {
            "patterns_analyzed": patterns_found,
            "new_patterns": new_patterns,
            "total_patterns": len(self.semantic_patterns)
        }
    
    def _identify_success_patterns(self) -> List[SemanticPattern]:
        """Identify patterns in successful objectives."""
        patterns = []
        
        if len(self.completed_objectives) < self.min_pattern_frequency:
            return patterns
        
        # Group objectives by keywords
        keyword_groups = defaultdict(list)
        
        for obj in self.completed_objectives:
            keywords = self._extract_keywords(obj["objective"])
            strategy = obj.get("strategy_used", "")
            
            for keyword in keywords:
                keyword_groups[keyword].append({
                    "objective": obj["objective"],
                    "strategy": strategy,
                    "date": obj["date"]
                })
        
        # Create patterns for frequently occurring keywords
        for keyword, instances in keyword_groups.items():
            if len(instances) >= self.min_pattern_frequency:
                pattern_id = f"success_{hashlib.md5(keyword.encode()).hexdigest()[:8]}"
                
                # Calculate success rate (all instances are successes)
                success_rate = 1.0
                confidence = min(len(instances) / 10.0, 1.0)  # More instances = higher confidence
                
                pattern = SemanticPattern(
                    pattern_id=pattern_id,
                    pattern_type="success_pattern",
                    pattern_keywords=[keyword],
                    success_rate=success_rate,
                    frequency=len(instances),
                    confidence=confidence,
                    first_seen=min(inst["date"] for inst in instances),
                    last_seen=max(inst["date"] for inst in instances),
                    examples=[inst["objective"][:100] for inst in instances[:3]]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _identify_failure_patterns(self) -> List[SemanticPattern]:
        """Identify patterns in failed objectives."""
        patterns = []
        
        if len(self.failed_objectives) < self.min_pattern_frequency:
            return patterns
        
        # Group objectives by failure reasons and keywords
        failure_groups = defaultdict(list)
        
        for obj in self.failed_objectives:
            keywords = self._extract_keywords(obj["objective"])
            reason = obj.get("reason", "unknown")
            
            # Group by reason + primary keyword
            for keyword in keywords[:2]:  # Focus on most important keywords
                group_key = f"{reason}_{keyword}"
                failure_groups[group_key].append({
                    "objective": obj["objective"],
                    "reason": reason,
                    "date": obj["date"]
                })
        
        # Create patterns for frequently occurring failure combinations
        for group_key, instances in failure_groups.items():
            if len(instances) >= self.min_pattern_frequency:
                pattern_id = f"failure_{hashlib.md5(group_key.encode()).hexdigest()[:8]}"
                
                # Calculate failure rate (all instances are failures)
                success_rate = 0.0
                confidence = min(len(instances) / 5.0, 1.0)  # Failures need fewer instances for confidence
                
                reason, keyword = group_key.split("_", 1)
                
                pattern = SemanticPattern(
                    pattern_id=pattern_id,
                    pattern_type="failure_pattern",
                    pattern_keywords=[keyword],
                    success_rate=success_rate,
                    frequency=len(instances),
                    confidence=confidence,
                    first_seen=min(inst["date"] for inst in instances),
                    last_seen=max(inst["date"] for inst in instances),
                    examples=[f"{inst['reason']}: {inst['objective'][:80]}" for inst in instances[:3]]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "should", "could", "can", "may", "might", "must"
        }
        
        # Extract words, convert to lowercase, remove punctuation
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency and return most common
        word_freq = Counter(keywords)
        return [word for word, _ in word_freq.most_common(5)]
    
    def _update_pattern_statistics(self):
        """Update statistics for existing patterns based on new data."""
        timestamp = self._get_timestamp()
        
        for pattern in self.semantic_patterns.values():
            # Update last_seen if pattern is still relevant
            pattern.last_seen = timestamp
    
    def learn_heuristics(self) -> Dict[str, Any]:
        """
        Learn heuristics from historical data about what works and what doesn't.
        """
        new_heuristics = 0
        updated_heuristics = 0
        
        # Learn strategy preferences
        strategy_heuristics = self._learn_strategy_heuristics()
        for heuristic in strategy_heuristics:
            if heuristic.heuristic_id not in self.learned_heuristics:
                new_heuristics += 1
            else:
                updated_heuristics += 1
            self.learned_heuristics[heuristic.heuristic_id] = heuristic
        
        # Learn sequence patterns
        sequence_heuristics = self._learn_sequence_heuristics()
        for heuristic in sequence_heuristics:
            if heuristic.heuristic_id not in self.learned_heuristics:
                new_heuristics += 1
            else:
                updated_heuristics += 1
            self.learned_heuristics[heuristic.heuristic_id] = heuristic
        
        # Learn contextual preferences
        context_heuristics = self._learn_context_heuristics()
        for heuristic in context_heuristics:
            if heuristic.heuristic_id not in self.learned_heuristics:
                new_heuristics += 1
            else:
                updated_heuristics += 1
            self.learned_heuristics[heuristic.heuristic_id] = heuristic
        
        return {
            "new_heuristics": new_heuristics,
            "updated_heuristics": updated_heuristics,
            "total_heuristics": len(self.learned_heuristics)
        }
    
    def _learn_strategy_heuristics(self) -> List[Heuristic]:
        """Learn which strategies work best for which types of objectives."""
        heuristics = []
        
        # Analyze strategy success rates
        strategy_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"successes": 0, "failures": 0, "contexts": []})
        
        for obj in self.completed_objectives:
            strategy = obj.get("strategy_used", "unknown")
            keywords = self._extract_keywords(obj["objective"])
            strategy_stats[strategy]["successes"] += 1
            strategy_stats[strategy]["contexts"].extend(keywords[:2])
        
        for obj in self.failed_objectives:
            # Try to infer strategy from failure reason or context
            strategy = self._infer_strategy_from_failure(obj)
            if strategy:
                keywords = self._extract_keywords(obj["objective"])
                strategy_stats[strategy]["failures"] += 1
                strategy_stats[strategy]["contexts"].extend(keywords[:2])
        
        # Create heuristics for strategies with clear patterns
        for strategy, stats in strategy_stats.items():
            total = stats["successes"] + stats["failures"]
            if total >= 3:  # Minimum evidence
                success_rate = stats["successes"] / total
                confidence = min(total / 10.0, 1.0)
                
                if success_rate >= 0.7:  # Prefer this strategy
                    heuristic_id = f"prefer_strategy_{hashlib.md5(strategy.encode()).hexdigest()[:8]}"
                    heuristics.append(Heuristic(
                        heuristic_id=heuristic_id,
                        rule_type="prefer",
                        condition=f"objective_type matches patterns for {strategy}",
                        action=f"prefer strategy: {strategy}",
                        success_rate=success_rate,
                        confidence=confidence,
                        evidence_count=total,
                        created_date=self._get_timestamp()
                    ))
                elif success_rate <= 0.3:  # Avoid this strategy
                    heuristic_id = f"avoid_strategy_{hashlib.md5(strategy.encode()).hexdigest()[:8]}"
                    heuristics.append(Heuristic(
                        heuristic_id=heuristic_id,
                        rule_type="avoid",
                        condition=f"objective_type matches patterns for {strategy}",
                        action=f"avoid strategy: {strategy}",
                        success_rate=success_rate,
                        confidence=confidence,
                        evidence_count=total,
                        created_date=self._get_timestamp()
                    ))
        
        return heuristics
    
    def _learn_sequence_heuristics(self) -> List[Heuristic]:
        """Learn patterns about sequences of objectives that work well together."""
        heuristics = []
        
        # Look for sequences in recent objectives log
        if len(self.recent_objectives_log) >= 3:
            sequences = []
            for i in range(len(self.recent_objectives_log) - 2):
                sequence = [
                    self.recent_objectives_log[i]["status"],
                    self.recent_objectives_log[i + 1]["status"],
                    self.recent_objectives_log[i + 2]["status"]
                ]
                sequences.append(sequence)
            
            # Find patterns in sequences
            sequence_counter = Counter([tuple(seq) for seq in sequences])
            
            for sequence, count in sequence_counter.items():
                if count >= 2:  # Recurring sequence
                    if sequence == ("success", "success", "success"):
                        heuristic_id = f"success_sequence_{hashlib.md5(str(sequence).encode()).hexdigest()[:8]}"
                        heuristics.append(Heuristic(
                            heuristic_id=heuristic_id,
                            rule_type="sequence",
                            condition="after two consecutive successes",
                            action="maintain current approach and strategy selection",
                            success_rate=1.0,
                            confidence=min(count / 5.0, 1.0),
                            evidence_count=count,
                            created_date=self._get_timestamp()
                        ))
                    elif sequence.count("failure") >= 2:
                        heuristic_id = f"failure_sequence_{hashlib.md5(str(sequence).encode()).hexdigest()[:8]}"
                        heuristics.append(Heuristic(
                            heuristic_id=heuristic_id,
                            rule_type="sequence",
                            condition="after multiple failures in sequence",
                            action="consider meta-analysis or capability development",
                            success_rate=0.0,
                            confidence=min(count / 3.0, 1.0),
                            evidence_count=count,
                            created_date=self._get_timestamp()
                        ))
        
        return heuristics
    
    def _learn_context_heuristics(self) -> List[Heuristic]:
        """Learn contextual patterns about when certain approaches work."""
        heuristics = []
        
        # Analyze time-based patterns
        hourly_success = defaultdict(lambda: {"successes": 0, "failures": 0})
        
        for obj in self.completed_objectives + self.failed_objectives:
            try:
                # Extract hour from timestamp
                date_obj = datetime.datetime.fromisoformat(obj["date"].replace("Z", "+00:00"))
                hour = date_obj.hour
                
                if obj in self.completed_objectives:
                    hourly_success[hour]["successes"] += 1
                else:
                    hourly_success[hour]["failures"] += 1
            except (ValueError, KeyError):
                continue
        
        # Create time-based heuristics if there are clear patterns
        for hour, stats in hourly_success.items():
            total = stats["successes"] + stats["failures"]
            if total >= 3:
                success_rate = stats["successes"] / total
                if success_rate >= 0.8 or success_rate <= 0.2:
                    heuristic_id = f"time_context_{hour}"
                    action = "prefer execution at this time" if success_rate >= 0.8 else "avoid execution at this time"
                    heuristics.append(Heuristic(
                        heuristic_id=heuristic_id,
                        rule_type="context",
                        condition=f"execution hour is {hour}",
                        action=action,
                        success_rate=success_rate,
                        confidence=min(total / 10.0, 1.0),
                        evidence_count=total,
                        created_date=self._get_timestamp()
                    ))
        
        return heuristics
    
    def _infer_strategy_from_failure(self, failed_obj: Dict[str, Any]) -> Optional[str]:
        """Infer what strategy was likely used based on failure reason."""
        reason = failed_obj.get("reason", "").lower()
        
        if "syntax" in reason:
            return "direct_implementation"
        elif "pytest" in reason or "test" in reason:
            return "pytest_validation"
        elif "timeout" in reason:
            return "complex_validation"
        elif "validation" in reason:
            return "sandbox_validation"
        
        return None
    
    def get_relevant_patterns(self, objective: str) -> List[SemanticPattern]:
        """Get patterns relevant to a specific objective."""
        keywords = self._extract_keywords(objective)
        relevant_patterns = []
        
        for pattern in self.semantic_patterns.values():
            # Check if any keywords match
            if any(keyword in pattern.pattern_keywords for keyword in keywords):
                relevant_patterns.append(pattern)
        
        # Sort by confidence and frequency
        relevant_patterns.sort(key=lambda p: (p.confidence, p.frequency), reverse=True)
        return relevant_patterns
    
    def get_applicable_heuristics(self, context: Dict[str, Any]) -> List[Heuristic]:
        """Get heuristics applicable to the current context."""
        applicable = []
        
        for heuristic in self.learned_heuristics.values():
            if heuristic.confidence >= self.min_confidence_threshold:
                # Simple context matching (can be enhanced)
                if self._matches_context(heuristic, context):
                    applicable.append(heuristic)
        
        # Sort by confidence and success rate
        applicable.sort(key=lambda h: (h.confidence, h.success_rate), reverse=True)
        return applicable
    
    def _matches_context(self, heuristic: Heuristic, context: Dict[str, Any]) -> bool:
        """Check if a heuristic matches the current context."""
        # Simplified context matching - can be enhanced with more sophisticated logic
        condition = heuristic.condition.lower()
        
        if "objective_type" in condition and "objective" in context:
            objective_keywords = self._extract_keywords(context["objective"])
            return any(keyword in condition for keyword in objective_keywords)
        
        if "strategy" in condition and "strategy" in context:
            return context["strategy"].lower() in condition
        
        if "hour" in condition and "current_time" in context:
            try:
                current_hour = context["current_time"].hour
                return str(current_hour) in condition
            except (AttributeError, KeyError):
                pass
        
        return False
    
    def get_enhanced_history_for_prompt(self, objective: str = "") -> str:
        """
        Get enhanced history including patterns and heuristics relevant to current objective.
        """
        base_history = self.get_full_history_for_prompt()
        
        enhancement_parts = [base_history]
        
        # Add relevant patterns
        if objective and self.semantic_patterns:
            relevant_patterns = self.get_relevant_patterns(objective)[:3]  # Top 3
            if relevant_patterns:
                enhancement_parts.append("\nRelevant Patterns:")
                for pattern in relevant_patterns:
                    enhancement_parts.append(
                        f"- {pattern.pattern_type}: {pattern.pattern_keywords} "
                        f"(Success Rate: {pattern.success_rate:.1%}, Confidence: {pattern.confidence:.1%})"
                    )
        
        # Add applicable heuristics
        if self.learned_heuristics:
            context = {"objective": objective}
            applicable_heuristics = self.get_applicable_heuristics(context)[:3]  # Top 3
            if applicable_heuristics:
                enhancement_parts.append("\nApplicable Heuristics:")
                for heuristic in applicable_heuristics:
                    enhancement_parts.append(
                        f"- {heuristic.rule_type.title()}: {heuristic.action} "
                        f"(Confidence: {heuristic.confidence:.1%})"
                    )
        
        # Add pattern summary
        if self.semantic_patterns or self.learned_heuristics:
            enhancement_parts.append(f"\nMemory Analytics: {len(self.semantic_patterns)} patterns, {len(self.learned_heuristics)} heuristics learned")
        
        return "\n".join(enhancement_parts)
    
    def trigger_pattern_learning(self):
        """Trigger pattern and heuristic learning after objective completion."""
        if self.pattern_recognition_enabled:
            self.analyze_semantic_patterns()
            self.learn_heuristics()

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    mem = Memory(filepath="temp_memory_test.json")
    mem.load() # Load existing or start fresh

    mem.add_completed_objective("Implement feature X", "direct_implementation", "Feature X implemented successfully and tested.")
    mem.add_failed_objective("Refactor module Y", "pytest_failure", "Refactoring led to test failures in dependent modules.")
    mem.add_capability("New web scraping tool added", related_objective="Implement feature X")

    print("Current History Summary:")
    print(mem.get_history_summary(max_items_per_category=2))

    print("\nFull History for Prompt:")
    print(mem.get_full_history_for_prompt())

    mem.save()
    print(f"\nMemory saved to {mem.filepath}")

    # Test loading
    mem2 = Memory(filepath="temp_memory_test.json")
    mem2.load()
    print("\nLoaded History Summary (from mem2):")
    print(mem2.get_history_summary(max_items_per_category=2))

    # Clean up the temporary file
    if os.path.exists("temp_memory_test.json"):
        os.remove("temp_memory_test.json")
        print("\nCleaned up temp_memory_test.json")
