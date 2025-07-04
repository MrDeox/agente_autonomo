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
# PerformanceAnalysisAgent is now in agent.agents
from agent.agents import PerformanceAnalysisAgent
from agent.utils.llm_client import call_llm_api
from agent.prompt_builder import (
    build_memory_context_section,
    build_initial_objective_prompt,
    build_meta_analysis_objective_prompt,
    build_standard_objective_prompt
)
from agent.memory import Memory
from agent.model_optimizer import ModelOptimizer


def generate_next_objective(
    model_config: Dict[str, str],
    current_manifest: str,
    logger: logging.Logger,
    project_root_dir: str,
    config: Optional[Dict[str, Any]] = None,
    memory: Optional[Memory] = None,
    model_optimizer: Optional[ModelOptimizer] = None,
    current_objective: Optional[str] = None
) -> str:
    """
    Generates the next evolutionary objective using code analysis and performance data.
    """
    if logger: logger.info("Generating next objective...")

    config = config or {}

    # Read strategic documents
    capabilities_content = ""
    try:
        with open("docs/CAPABILITIES.md", "r", encoding="utf-8") as f:
            capabilities_content = f.read()
        if logger: logger.info("docs/CAPABILITIES.md lido com sucesso.")
    except FileNotFoundError:
        if logger: logger.warning("docs/CAPABILITIES.md não encontrado.")
        capabilities_content = "CAPABILITIES.md não encontrado."
    except Exception as e:
        if logger: logger.error(f"Erro ao ler docs/CAPABILITIES.md: {e}")
        capabilities_content = f"Erro ao ler CAPABILITIES.md: {e}"

    roadmap_content = ""
    try:
        with open("docs/ROADMAP.md", "r", encoding="utf-8") as f:
            roadmap_content = f.read()
        if logger: logger.info("docs/ROADMAP.md lido com sucesso.")
    except FileNotFoundError:
        if logger: logger.warning("docs/ROADMAP.md não encontrado.")
        roadmap_content = "ROADMAP.md não encontrado."
    except Exception as e:
        if logger: logger.error(f"Erro ao ler docs/ROADMAP.md: {e}")
        roadmap_content = f"Erro ao ler ROADMAP.md: {e}"

    # 1. Analyze code metrics using thresholds from config
    code_analysis_summary_str = ""
    try:
        if logger: logger.info(f"Analyzing code metrics in: {project_root_dir}")

        cfg = config or {}
        # Get thresholds from config, with defaults
        thresholds = cfg.get("code_analysis_thresholds", {})
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

    # 2. Analyze performance from ModelOptimizer
    performance_summary_str = ""
    if model_optimizer:
        try:
            if logger: logger.info("Analyzing agent performance from ModelOptimizer...")
            agent_perf = model_optimizer.get_agent_performance_summary()
            if agent_perf:
                perf_lines = ["Agent Performance Summary (Success Rate | Avg. Quality Score):"]
                for agent, stats in agent_perf.items():
                    perf_lines.append(f"  - {agent}: {stats.get('success_rate', 'N/A')*100:.1f}% | {stats.get('average_quality_score', 'N/A'):.2f}")
                performance_summary_str = "\\n".join(perf_lines)
            else:
                performance_summary_str = "No agent performance data available."
            if logger: logger.debug(f"Performance analysis summary:\\n{performance_summary_str}")
        except Exception as e:
            if logger: logger.error(f"Error analyzing performance: {e}", exc_info=True)
            performance_summary_str = "Error processing performance analysis."

    # 3. Prepare manifest and memory context
    current_manifest = current_manifest or "" # Ensure not None
    memory_context_section = ""
    if memory:
        memory_context_section = build_memory_context_section(memory.get_full_history_for_prompt())

    # 4. Build the prompt using functions from prompt_builder
    prompt: str
    if not current_manifest.strip() and not code_analysis_summary_str.strip(): # First cycle, no analysis
        prompt = build_initial_objective_prompt(memory_context_section)
    else:
        if current_objective and current_objective.startswith("[META-ANALYSIS OBJECTIVE]"):
            logger.info(f"Meta-analysis objective detected: {current_objective}")
            match = re.search(r'The objective \"(.*?)\" failed repeatedly due to \"(.*?)\"', current_objective)
            original_failed_objective = match.group(1) if match else "N/A"
            error_reason_for_meta = match.group(2) if match else "N/A"
            prompt = build_meta_analysis_objective_prompt(
                current_objective=current_objective,
                original_failed_objective=original_failed_objective,
                error_reason_for_meta=error_reason_for_meta,
                performance_summary_str=performance_summary_str,
                memory_context_section=memory_context_section,
                capabilities_content=capabilities_content,
                roadmap_content=roadmap_content
            )
        else:
            prompt = build_standard_objective_prompt(
                memory_context_section=memory_context_section,
                performance_summary_str=performance_summary_str,
                code_analysis_summary_str=code_analysis_summary_str,
                current_manifest=current_manifest,
                capabilities_content=capabilities_content,
                roadmap_content=roadmap_content
            )

    if logger: logger.debug(f"Prompt for generate_next_objective:\n{prompt}")

    # 4. Call LLM API using the centralized function
    content, error = call_llm_api(
        model_config=model_config,
        prompt=prompt,
        temperature=0.3,
        logger=logger
    )

    if error:
        log_message = f"Erro ao gerar próximo objetivo: {error}"
        if logger:
            logger.error(log_message)
        return "Analisar o estado atual do projeto e propor uma melhoria incremental"

    if not content: # Content can be an empty string, which is a valid (though poor) objective
        log_message = "Resposta vazia do LLM para próximo objetivo."
        if logger:
            logger.warning(log_message)
        return "Analisar o estado atual do projeto e propor uma melhoria incremental"

    return content.strip()


def generate_capacitation_objective(
    model_config: Dict[str, str],
    engineer_analysis: str,
    memory_summary: Optional[str] = None,
    logger: Optional[logging.Logger] = None # Changed type hint
) -> str:
    """Generates an objective to create necessary new capabilities."""
    memory_context_str = ""
    if memory_summary and memory_summary.strip() and memory_summary.lower() != "no relevant history available.":
        memory_context_str = f"""
[HISTÓRICO RECENTE DO AGENTE]
{memory_summary}
Check if any similar capability has been attempted or implemented recently.
"""

    prompt = f"""
[Context]
You are the Capacitation Planner for the Hephaestus agent. An engineer proposed a solution that requires new tools/capabilities that do not exist or were previously insufficient.
{memory_context_str}
Análise do Engenheiro que Requer Nova Capacidade
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

    content, error = call_llm_api(
        model_config=model_config,
        prompt=prompt,
        temperature=0.3,
        logger=logger
    )

    if error:
        log_message = f"Erro ao gerar objetivo de capacitação: {error}"
        if logger:
            logger.error(log_message)
        return "Analisar a necessidade de capacitação e propor uma solução"

    if not content:
        log_message = "Empty response from LLM for capacitation objective."
        if logger:
            logger.warning(log_message)
        return "Analisar a necessidade de capacitação e propor uma solução"

    return content.strip()


def generate_commit_message(
    analysis_summary: str,
    objective: str,
    logger: logging.Logger, # Changed type hint
) -> str:
    """
    Generates a concise and informative commit message using a rule-based system.
    
    Args:
        analysis_summary: Summary of the analysis and implementation of the change. (Not currently used, but kept for API consistency)
        objective: The original objective of the change.
        logger: Logger instance for recording information.

    Returns:
        A string containing the generated commit message.
    """

    logger.info("Generating commit message with rule-based system...")

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
    if commit_type == "refactor":
        max_summary_len += 2

    if len(short_summary) > max_summary_len:
        trunc_len = max_summary_len - 3
        short_summary = short_summary[:trunc_len] + "..."

    commit_message = f"{commit_type}: {short_summary}"

    logger.info(f"Commit message generated: {commit_message}")
    return commit_message