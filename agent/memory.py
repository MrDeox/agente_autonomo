import json
import datetime
import os
from typing import List, Dict, Any, Optional
from datetime import timezone # Adicionado

class Memory:
    """
    Manages persistent memory for the Hephaestus agent, storing historical data
    about objectives, failures, and acquired capabilities.
    """
    def __init__(self, filepath: str = "HEPHAESTUS_MEMORY.json", max_objectives_history: int = 20):
        """
        Initializes the Memory module.

        Args:
            filepath: The path to the JSON file used for storing memory.
            max_objectives_history: The maximum number of objectives to keep in history.
        """
        self.filepath: str = filepath
        self.max_objectives_history: int = max_objectives_history
        self.completed_objectives: List[Dict[str, Any]] = []
        self.failed_objectives: List[Dict[str, Any]] = []
        self.acquired_capabilities: List[Dict[str, Any]] = []
        self.recent_objectives_log: List[Dict[str, Any]] = [] # Novo atributo
        self.cycle_count: int = 0
        # knowledge_summary can be added later if needed.

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
            "recent_objectives_log": self.recent_objectives_log # Salvar novo atributo
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
            "date": self._get_timestamp()
        }
        self.completed_objectives.append(record)
        self._add_to_recent_objectives_log(objective, "success")

    def _add_to_recent_objectives_log(self, objective: str, status: str) -> None:
        """Helper method to add to the recent objectives log and keep it trimmed."""
        log_entry = {
            "objective": objective,
            "status": status,
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

        all_objectives = self.completed_objectives + self.failed_objectives

        # Remove duplicates, keeping the most recent entry for the same objective description
        # We sort by date first (older to newer) so that when we encounter duplicates,
        # the one added to unique_objectives_dict will be the latest one.
        all_objectives.sort(key=lambda x: x["date"])

        unique_objectives_dict: Dict[str, Dict[str, Any]] = {}
        for obj in all_objectives:
            # Using 'objective' field as the key for deduplication
            unique_objectives_dict[obj["objective"]] = obj

        # Convert back to list and sort by date (most recent first)
        processed_objectives = sorted(
            list(unique_objectives_dict.values()),
            key=lambda x: x["date"],
            reverse=True
        )

        # Keep only the last max_objectives_history objectives
        kept_objectives = processed_objectives[:self.max_objectives_history]

        # Separate back into completed and failed objectives
        self.completed_objectives = [
            obj for obj in kept_objectives if obj in self.completed_objectives
        ]
        self.failed_objectives = [
            obj for obj in kept_objectives if obj in self.failed_objectives
        ]

        # Note: This logic for separating back might not be perfect if an objective string
        # could exist in both completed and failed (which shouldn't happen with current add methods).
        # A more robust way would be to check the original list or add a 'status' field
        # when combining them. For now, this assumes objective strings are unique enough
        # or that the original lists are the source of truth for status.
        # A simpler approach for separation, assuming objective dicts are unique by content:
        new_completed = []
        new_failed = []
        original_completed_set = {json.dumps(o, sort_keys=True) for o in self.completed_objectives}
        original_failed_set = {json.dumps(o, sort_keys=True) for o in self.failed_objectives}

        for obj in kept_objectives:
            obj_dump = json.dumps(obj, sort_keys=True)
            if obj_dump in original_completed_set:
                new_completed.append(obj)
            elif obj_dump in original_failed_set:
                new_failed.append(obj)

        # Sort chronologically before assigning
        self.completed_objectives = sorted(new_completed, key=lambda x: x["date"])
        self.failed_objectives = sorted(new_failed, key=lambda x: x["date"])


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
            "date": self._get_timestamp()
        }
        self.failed_objectives.append(record)
        self._add_to_recent_objectives_log(objective, "failure")

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
