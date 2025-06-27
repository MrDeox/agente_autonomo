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
            "date": self._get_timestamp(),
            "status": "completed"  # Adicionado status
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
