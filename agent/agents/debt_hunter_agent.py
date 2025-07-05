import logging
from typing import Dict, Any, Optional

from agent.project_scanner import analyze_code_metrics
from agent.utils.llm_client import call_llm_api

class DebtHunterAgent:
    """
    An autonomous agent that proactively hunts for technical debt and proposes
    refactoring or testing objectives.
    """
    def __init__(self, model_config: Dict[str, Any], config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger

    def hunt_for_debt(self, project_root_dir: str = ".") -> Optional[str]:
        """
        Analyzes the codebase for technical debt and generates a refactoring objective.

        Returns:
            A string containing a single, actionable objective, or None if no significant
            debt is found.
        """
        self.logger.info("🕵️ Debt Hunter Agent: Starting hunt for technical debt...")

        try:
            # 1. Analyze code metrics to find debt hotspots
            thresholds = self.config.get("code_analysis_thresholds", {})
            analysis_results = analyze_code_metrics(
                root_dir=project_root_dir,
                file_loc_threshold=thresholds.get("file_loc", 300),
                func_loc_threshold=thresholds.get("function_loc", 50),
                func_cc_threshold=thresholds.get("function_cc", 10)
            )
            
            code_analysis_summary = self._format_analysis_summary(analysis_results.get("summary", {}))

            if "No notable code metrics" in code_analysis_summary:
                self.logger.info("Debt Hunter Agent: No significant technical debt found. Hunt complete.")
                return None
            
            self.logger.info(f"Debt Hunter Agent: Found potential debt hotspots:\\n{code_analysis_summary}")

            # 2. Use LLM to decide on the most impactful objective
            prompt = self._build_debt_analysis_prompt(code_analysis_summary)
            
            objective, error = call_llm_api(
                model_config=self.model_config,
                prompt=prompt,
                temperature=0.3,
                logger=self.logger
            )

            if error:
                self.logger.error(f"Debt Hunter Agent: LLM call failed: {error}")
                return None
            
            if not objective:
                self.logger.warning("Debt Hunter Agent: LLM generated an empty objective.")
                return None

            self.logger.info(f"Debt Hunter Agent: Proposed objective: {objective.strip()}")
            return objective.strip()

        except Exception as e:
            self.logger.error(f"An unexpected error occurred during debt hunt: {e}", exc_info=True)
            return None

    def _format_analysis_summary(self, summary_data: Dict[str, Any]) -> str:
        """Formats the code analysis summary for the LLM prompt."""
        sections = []
        if summary_data.get("large_files"):
            sections.append("Large Files (potential candidates for modularization):")
            for path, loc in summary_data["large_files"]: sections.append(f"  - {path} (LOC: {loc})")
        if summary_data.get("large_functions"):
            sections.append("\\nLarge Functions (potential candidates for refactoring/splitting):")
            for path, name, loc in summary_data["large_functions"]: sections.append(f"  - {path} -> {name}() (LOC: {loc})")
        if summary_data.get("complex_functions"):
            sections.append("\\nComplex Functions (high CC, candidates for refactoring):")
            for path, name, cc in summary_data["complex_functions"]: sections.append(f"  - {path} -> {name}() (CC: {cc})")
        if summary_data.get("missing_tests"):
            sections.append("\\nModules without Corresponding Test Files (candidates for test creation):")
            for path in summary_data["missing_tests"]: sections.append(f"  - {path}")
        
        return "\\n".join(sections) if sections else "No notable code metrics were identified."

    def _build_debt_analysis_prompt(self, code_analysis_summary: str) -> str:
        """Builds the prompt for the LLM to decide on a refactoring objective."""
        return f"""
[IDENTITY]
You are the "Debt Hunter," a specialized agent within the Hephaestus system. Your mission is to proactively identify and prioritize technical debt to ensure the long-term health and maintainability of the codebase.

[CONTEXT]
You have just completed a scan of the project and identified the following technical debt hotspots.

[CODE METRICS AND ANALYSIS]
{code_analysis_summary}

[YOUR TASK]
Based on the analysis, choose the SINGLE MOST IMPACTFUL technical debt to address right now. Prioritize in this order:
1.  **High Complexity (High CC):** Reducing complexity in critical functions is the top priority.
2.  **Missing Tests for Critical Modules:** Ensure core components are well-tested.
3.  **Large Files/Modules:** Break down monolithic files to improve modularity.

Generate a clear, concise, and actionable objective for the main Hephaestus agent to execute. The objective should be a single command.

[Example Objectives]
- "Refactor the function `generate_next_objective` in `agent/brain.py` (CC: 12) to reduce its cyclomatic complexity."
- "Create a new test file `tests/agent/project_scanner.py` with basic unit tests for the `analyze_code_metrics` function."
- "The module `agent/hephaestus_agent.py` is too large (LOC: 1048). Propose a refactoring plan to split it into smaller, more focused modules."

[OUTPUT FORMAT]
Respond ONLY with the text string of the single, most important objective.
""" 