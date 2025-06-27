# import logging # Already imported below
from typing import Optional, Any, Tuple, Dict, List # Added Dict, List
# import json # Already imported below
# import requests # No longer needed here
from datetime import datetime
import json
import logging
import re
# import requests # No longer needed here, call_llm_api is now in llm_client
# import traceback # No longer directly used here, but llm_client might use it
# from typing import Optional, Dict, Any, List, Tuple # Already imported above

# parse_json_response is in agent/agents.py (or could be in utils)
# get_action_plan is in ArchitectAgent.plan_action
# call_llm_api is imported from agent.utils.llm_client
# get_maestro_decision is in MaestroAgent.choose_strategy

# Functions remaining in brain.py:
# - generate_next_objective
# - generate_capacitation_objective
# - generate_commit_message

from agent.project_scanner import analyze_code_metrics
from agent.utils.llm_client import call_llm_api


def generate_next_objective(
    api_key: str,
    model: str,
    current_manifest: str,
    logger: logging.Logger, # Changed type hint from Any
    project_root_dir: str,
    config: Dict[str, Any] | None = None,
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None
) -> str:
    """
    Generates the next evolutionary objective using a lightweight model and code analysis.
    """
    if logger: logger.info("Generating next objective...")

    config = config or {}

    # 1. Analyze code metrics using thresholds from config
    code_analysis_summary_str = ""
    try:
        if logger: logger.info(f"Analyzing code metrics in: {project_root_dir}")

        # Get thresholds from config, with defaults
        thresholds = config.get("code_analysis_thresholds", {})
        file_loc_threshold = thresholds.get("file_loc", 300)
        func_loc_threshold = thresholds.get("function_loc", 50)
        func_cc_threshold = thresholds.get("function_cc", 10)

        analysis_results = analyze_code_metrics(
            root_dir=project_root_dir,
            file_loc_threshold=file_loc_threshold,
            func_loc_threshold=func_loc_threshold,
            func_cc_threshold=func_cc_threshold
        )

        summary_data = analysis_results.get("summary", {})
        sections = []

        if summary_data.get("large_files"):
            sections.append("Large Files (potential candidates for modularization):")
            for path, loc in summary_data["large_files"]:
                sections.append(f"  - {path} (LOC: {loc})")

        if summary_data.get("large_functions"):
            sections.append("\nLarge Functions (potential candidates for refactoring/splitting):")
            for path, name, loc in summary_data["large_functions"]:
                sections.append(f"  - {path} -> {name}() (LOC: {loc})")

        if summary_data.get("complex_functions"):
            sections.append("\nComplex Functions (high CC, potential candidates for refactoring/simplification):")
            for path, name, cc in summary_data["complex_functions"]:
                sections.append(f"  - {path} -> {name}() (CC: {cc})")

        if summary_data.get("missing_tests"):
            sections.append("\nModules without Corresponding Test Files (consider creating tests):")
            for path in summary_data["missing_tests"]:
                sections.append(f"  - {path}")

        if not sections:
            code_analysis_summary_str = "No notable code metrics (large files, complex/large functions, or missing tests) were identified with the current thresholds."
        else:
            code_analysis_summary_str = "\n".join(sections)

        if logger: logger.debug(f"Code analysis summary:\n{code_analysis_summary_str}")

    except Exception as e:
        if logger: logger.error(f"Error analyzing code metrics: {e}", exc_info=True)
        code_analysis_summary_str = "Error processing code analysis."


    # 2. Prepare manifest and memory context
    current_manifest = current_manifest or "" # Ensure not None
    sanitized_memory = memory_summary.strip() if memory_summary and memory_summary.strip() else None
    memory_context_section = ""
    if sanitized_memory and sanitized_memory.lower() != "no relevant history available.":
        memory_context_section = f"""
[RECENT PROJECT AND AGENT HISTORY (Hephaestus)]
{sanitized_memory}
Consider this history to avoid repeating failures, build on successes, and identify gaps.
"""
    # 3. Build the prompt
    if not current_manifest.strip() and not code_analysis_summary_str.strip(): # First cycle, no analysis
        prompt_template = """
[Context]
You are the 'Strategic Planner' of the autonomous AI agent Hephaestus. This is the first execution cycle, the project manifest does not yet exist, and code analysis has not returned significant data. Your task is to propose an initial objective to create basic project documentation or perform an initial analysis.
{memory_section}
[Examples of First Objectives]
- "Create the AGENTS.md file with the basic project structure."
- "Document the main interfaces in the project manifest."
- "Describe the basic agent architecture in the manifest."
- "Perform an initial scan to identify the main project components."

[Your Task]
Generate ONLY a single text string containing the initial objective. Be concise and direct.
"""
        prompt = prompt_template.format(memory_section=memory_context_section)
    else:
        prompt_template = """
[Main Context]
You are the 'Advanced Strategic Planner' of the autonomous AI agent Hephaestus. Your primary responsibility is to identify and propose the next most impactful development objective for the evolution of the agent or the project under analysis.

[Decision Process for the Next Objective]
1.  **Analyze Code Metrics:** Review the `[CODE METRICS AND ANALYSIS]` section below. It contains data on file size (LOC), function size (LOC), cyclomatic complexity (CC) of functions, and modules that may be missing tests.
2.  **Consider the Project Manifest:** If the `[CURRENT PROJECT MANIFEST]` is provided, use it to understand the overall goals, architecture, and areas already documented or needing attention.
3.  **Review Recent History:** The `[RECENT PROJECT AND AGENT HISTORY]` section provides context on recent tasks, successes, and failures. Avoid repeating objectives that recently failed in the same way, unless the cause of failure has been resolved. Use history to build on successes.
4.  **Prioritize Structural and Quality Improvements:** Based on metrics, identify opportunities to:
    *   Refactor very large modules or very long/complex functions.
    *   Create tests for critical/complex modules or functions that lack them.
    *   Improve documentation (docstrings, manifest) where crucial.
    *   Propose the creation of new capabilities (new agents, tools) if the analysis indicates a strategic need.
5.  **Be Specific and Actionable:** The objective should be clear, concise, and indicate a concrete action.

{memory_section}

[CODE METRICS AND ANALYSIS]
{code_analysis_summary}

[CURRENT PROJECT MANIFEST (if existing)]
{current_manifest}

[Examples of Smart and Self-Aware Objectives]
*   **Metrics-Based Refactoring:**
    *   "Refactor the module `agent/brain.py` (LOC: 350) which is extensive, considering splitting responsibilities into smaller modules (e.g., `agent/prompt_builder.py` or `agent/analysis_processor.py`)."
    *   "The function `generate_next_objective` in `agent/brain.py` (LOC: 85, CC: 12) is long and complex. Propose a plan to refactor it into smaller, more focused functions."
    *   "Analyze the most complex functions (CC > 10) listed in the metrics and select one for refactoring."
*   **Test Creation:**
    *   "The module `agent/project_scanner.py` (LOC: 280) does not have a corresponding test file `tests/agent/test_project_scanner.py`. Create unit tests for the `analyze_code_metrics` function."
    *   "The function `call_llm_api` (formerly `_call_llm_api`) is critical. Ensure robust unit tests exist for it, covering success and failure cases."
*   **Strategic Documentation Improvement:**
    *   "The manifest (`AGENTS.md`) does not describe the new metrics analysis functionality in `project_scanner.py`. Update it."
    *   "Improve docstrings for public functions in the `agent/memory.py` module to detail parameters and expected behavior."
*   **Development of New Capabilities (Agents/Tools):**
    *   "Create a new agent (e.g., `CodeQualityAgent` in `agent/agents.py`) dedicated to continuously monitoring code quality metrics and reporting regressions."
    *   "Develop a new tool in `agent/tool_executor.py` to automatically validate the syntax of JSON files before processing."
    *   "Propose a system for Hephaestus to evaluate the performance of its own operations and identify bottlenecks."
*   **Generic Objectives (when metrics/manifest are insufficient):**
    *   "Analyze the `agent/state.py` module to identify potential improvements in clarity or efficiency."
    *   "Review recent logs for frequent errors and propose an objective to fix them."

[Your Task]
Based on ALL the information provided (metrics, manifest, history), generate ONLY a single text string containing the NEXT STRATEGIC OBJECTIVE. The objective should be the most impactful and logical for the project's evolution at this moment.
Be concise, but specific enough to be actionable.
"""
        prompt = prompt_template.format(
            memory_section=memory_context_section,
            code_analysis_summary=code_analysis_summary_str,
            current_manifest=current_manifest if current_manifest.strip() else "N/A (Manifesto non-existent or empty)"
        )

    if logger: logger.debug(f"Prompt for generate_next_objective:\n{prompt}")

    # 4. Call LLM API using the centralized function
    content, error = call_llm_api(
        api_key=api_key,
        model=model,
        prompt=prompt,
        temperature=0.3,
        base_url=base_url,
        logger=logger
    )

    if error:
        log_message = f"Error generating next objective: {error}"
        if logger:
            logger.error(log_message)
        # else: print(log_message) # Avoid direct print
        return "Analyze current project state and propose an incremental improvement" # Fallback

    if not content: # Content can be an empty string, which is a valid (though poor) objective
        log_message = "Empty response from LLM for next objective."
        if logger:
            logger.warning(log_message)
        # else: print(log_message) # Avoid direct print
        return "Analyze current project state and propose an incremental improvement" # Fallback

    return content.strip()


def generate_capacitation_objective(
    api_key: str,
    model: str,
    engineer_analysis: str,
    base_url: str = "https://openrouter.ai/api/v1",
    memory_summary: Optional[str] = None,
    logger: Optional[logging.Logger] = None # Changed type hint
) -> str:
    """Generates an objective to create necessary new capabilities."""
    memory_context_str = ""
    if memory_summary and memory_summary.strip() and memory_summary.lower() != "no relevant history available.":
        memory_context_str = f"""
[RECENT AGENT HISTORY (Hephaestus)]
{memory_summary}
Check if any similar capability has been attempted or implemented recently.
"""

    prompt = f"""
[Context]
You are the Capacitation Planner for the Hephaestus agent. An engineer proposed a solution that requires new tools/capabilities that do not exist or were previously insufficient.
{memory_context_str}
[Engineer's Analysis Requiring New Capability]
{engineer_analysis}

[Your Task]
Translate the need described in the analysis into a clear, concise, and actionable engineering objective to create or enhance the missing capability. The objective should be an instruction for the Hephaestus agent itself to modify or add new tools/functions.
Consider the history to avoid repeating identical capacitation suggestions if they failed or if they were already successful and the analysis indicates a new need.

[Example Capacitation Objective]
If the analysis says "we need a tool to make GET web requests", your output could be: "Add a new function `http_get(url: str) -> str` to `agent/tool_executor.py` that uses the `requests` library to make GET requests and return the response content as a string."
If the analysis says "the JSON parsing function failed with large files", your output could be: "Improve the `parse_json_file` function in `agent/utils.py` to handle data streaming or increase efficiency for large JSON files."


[REQUIRED FORMAT]
Generate ONLY the text string of the new capacitation objective.
The objective MUST start with "[CAPACITATION TASK]". For example: "[CAPACITATION TASK] Add new tool X."
"""
    
    if logger:
        logger.debug(f"Prompt to generate capacitation objective:\n{prompt}")

    content, error = call_llm_api(api_key, model, prompt, 0.3, base_url, logger) # Use imported function

    if error:
        log_message = f"Error generating capacitation objective: {error}"
        if logger:
            logger.error(log_message)
        # else: print(log_message) # Avoid direct print
        return "Analyze capacitation need and propose a solution" # Fallback

    if not content:
        log_message = "Empty response from LLM for capacitation objective."
        if logger:
            logger.warning(log_message)
        # else: print(log_message) # Avoid direct print
        return "Analyze capacitation need and propose a solution" # Fallback

    return content.strip()


def generate_commit_message(
    api_key: str,
    model: str,
    analysis_summary: str,
    objective: str,
    logger: logging.Logger, # Changed type hint
    base_url: str = "https://openrouter.ai/api/v1"
) -> str:
    """
    Generates a concise and informative commit message using an LLM.
    (Currently simulated for this environment)

    Args:
        api_key: API key (e.g., OpenRouter).
        model: LLM model to use.
        analysis_summary: Summary of the analysis and implementation of the change.
        objective: The original objective of the change.
        logger: Logger instance for recording information.
        base_url: Base URL of the LLM API.

    Returns:
        A string containing the generated commit message.
        Returns a fallback message in case of error.
    """
    prompt = f"""
[Context] You are a software engineer writing a commit message for a change that has just been validated and applied.
[Objective of the Change]
{objective}
[Analysis/Summary of Implementation]
{analysis_summary}
[Your Task]
Based on the objective and analysis, write a clear and concise commit message following the 'Conventional Commits' standard. E.g., feat: Add benchmark tool or fix: Correct syntax validation for JSON. The message should be only the commit string, without prefixes or explanations.
"""

    logger.info(f"Generating commit message with model: {model}...")

    # This part remains a simulation as per the original code's intent for this function.
    # If direct LLM call is desired here, it should use call_llm_api.

    objective_lower = objective.lower()
    commit_type = "feat"  # Default
    commit_message_summary = objective # Use full objective initially for summary
    
    # Check if objective already has a conventional commit type prefix
    conventional_types = ["feat", "fix", "build", "chore", "ci", "docs", "style", "refactor", "perf", "test"]
    detected_type = None
    for conv_type in conventional_types:
        if objective_lower.startswith(conv_type + ":"):
            detected_type = conv_type
            # Remove the type prefix from the summary part
            commit_message_summary = objective[len(conv_type)+1:].strip()
            break

    if detected_type:
        commit_type = detected_type
    else:
        def find_word(words: list[str]) -> str | None:
            for w in words:
                if re.search(rf"\b{re.escape(w)}\b", objective_lower):
                    return w
            return None

        if (w := find_word(["add", "create", "implement", "introduce", "functionality", "feature", "capability"])):
            commit_type = "feat"
        elif (match := re.search(r"\b(fix|bug|issue|problem|resolve|correct)\b", objective_lower)):
            commit_type = "fix"
            w = match.group(1)
        elif (w := find_word(["refactor", "restructure", "reorganize", "cleanup"])):
            commit_type = "refactor"
        elif (w := find_word(["doc", "document", "documentation", "readme"])):
            commit_type = "docs"
        elif (w := find_word(["test", "tests", "testing"])):
            commit_type = "test"
        elif (w := find_word(["build", "ci", "pipeline", "config", "setup", "dependency", "dependencies"])):
            commit_type = "build"
        elif (w := find_word(["chore", "maintenance", "housekeeping", "style", "format"])):
            commit_type = "chore"
        else:
            w = None

        if w and objective_lower.startswith(w + " "):
            commit_message_summary = objective[len(w):].lstrip()
        # Add more heuristics if needed

    # Clean and truncate the summary part
    short_summary = commit_message_summary.replace('\n', ' ').replace('\r', '').strip()

    # Max length for the summary part of the commit message
    # Total conventional commit subject line is often recommended to be <= 72 chars.
    # Type + colon + space = len(commit_type) + 2
    max_summary_len = 72 - (len(commit_type) + 2)

    if len(short_summary) > max_summary_len:
        trunc_len = max_summary_len - 3
        if commit_type == "refactor":
            trunc_len = max_summary_len - 1
        short_summary = short_summary[:trunc_len] + "..."

    simulated_commit_message = f"{commit_type}: {short_summary}"

    logger.info(f"Commit message generated (simulated): {simulated_commit_message}")
    return simulated_commit_message

    # Original LLM call code (commented out):
    # content, error = call_llm_api(api_key, model, prompt, 0.5, base_url, logger)
    # if error:
    #     logger.error(f"Error generating commit message: {error}")
    #     return f"chore: Automatic updates based on objective: {objective}" # Fallback
    # if not content:
    #     logger.warning("Empty LLM response for commit message.")
    #     return f"chore: Automatic updates (empty LLM response): {objective}" # Fallback
    # return content.strip()
