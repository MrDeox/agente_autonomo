# Este módulo conterá funções para construir os diversos prompts
# usados pela função generate_next_objective em agent/brain.py.

from typing import Optional

def build_memory_context_section(memory_summary: Optional[str]) -> str:
    """
    Constrói a seção de contexto da memória para os prompts.
    """
    sanitized_memory = memory_summary.strip() if memory_summary and memory_summary.strip() else None
    memory_context_section = ""
    if sanitized_memory and sanitized_memory.lower() != "no relevant history available.":
        memory_context_section = f"""
[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]
{sanitized_memory}
Consider this history to avoid repeating failures, build on successes, and identify gaps.
"""
    return memory_context_section


def build_initial_objective_prompt(memory_context_section: str) -> str:
    """
    Constrói o prompt para gerar o objetivo inicial quando não há manifesto ou análise de código.
    """
    prompt_template = """
[Context]
You are the 'Planejador Estratégico' do agente autônomo Hephaestus. Este é o primeiro ciclo de execução, o manifesto do projeto ainda não existe e a análise de código não retornou dados significativos. Sua tarefa é propor um objetivo inicial para criar documentação básica do projeto ou realizar uma análise inicial.
{memory_section}
[Examples of First Objectives]
- "Create the AGENTS.md file with the basic project structure."
- "Document the main interfaces in the project manifest."
- "Describe the basic agent architecture in the manifest."
- "Perform an initial scan to identify the main project components."

[Your Task]
Generate ONLY a single text string containing the initial objective. Be concise and direct.
"""
    return prompt_template.format(memory_section=memory_context_section)


def build_meta_analysis_objective_prompt(
    current_objective: str,
    original_failed_objective: str,
    error_reason_for_meta: str,
    performance_summary_str: str,
    memory_context_section: str,
    capabilities_content: str,
    roadmap_content: str
) -> str:
    """
    Constrói o prompt para gerar um objetivo estratégico após uma meta-análise de falha.
    """
    meta_analysis_prompt_template = f"""
[Main Context]
You are the 'Meta-Strategic Planner' for the Hephaestus agent. Your task is to perform a deep meta-analysis of a previous failure and propose a new, more strategic objective to address the root cause, rather than just fixing the symptom.

[META-ANALYSIS OBJECTIVE]
{current_objective}

[ORIGINAL FAILED OBJECTIVE]
{original_failed_objective}

[REASON FOR FAILURE (from ErrorAnalysisAgent)]
{error_reason_for_meta}

[PERFORMANCE ANALYSIS (Overall Agent Performance)]
{performance_summary_str}

{memory_context_section}

[CAPABILITIES DOCUMENT (CAPABILITIES.md)]
{capabilities_content}

[ROADMAP DOCUMENT (ROADMAP.md)]
{roadmap_content}

[YOUR TASK]
Based on the meta-analysis objective, the original failure details, strategic documents (Capabilities, Roadmap), and the overall agent performance and history:

[YOUR TASK]
Based on the meta-analysis objective, the original failure details, and the overall agent performance and history:
1.  **Identify the root cause:** Was the original objective fundamentally flawed? Was the chosen strategy inappropriate? Was there a missing capability or tool?
2.  **Propose a new, strategic objective:** This objective should aim to prevent similar failures in the future by addressing the root cause. It could involve:
    *   Refining the prompt of an agent (e.g., Architect, Maestro, ErrorAnalysis).
    *   Proposing a new validation strategy.
    *   Suggesting the development of a new tool or capability.
    *   Revising the original objective with a different approach.
    *   Updating the project's `CAPABILITIES.md` or `ROADMAP.md`.

[Examples of Strategic Objectives from Meta-Analysis]
*   "The objective 'Implement feature X' failed due to repeated syntax errors. Propose a new validation strategy in `hephaestus_config.json` called 'PRE_COMMIT_LINTING' that runs `ruff` before any patches are applied."
*   "The objective 'Refactor module Y' failed because the MaestroAgent consistently chose an inadequate validation strategy. Analyze the MaestroAgent's prompt and propose modifications to improve its strategy selection for refactoring tasks."
*   "The objective 'Add new tool Z' failed due to a `TOOL_ERROR`. Analyze `agent/tool_executor.py` and propose a capacitation objective to enhance its error handling or add a missing dependency check for tool execution."
*   "The objective 'Improve documentation' failed repeatedly. Analyze the `DOC_UPDATE_STRATEGY` and propose a new objective to refine the prompt for the ArchitectAgent when generating documentation patches, focusing on clarity and completeness."
*   "The objective 'Implement feature A' failed due to a fundamental misunderstanding of the project's architecture. Propose an objective to update the `AGENTS.md` or `MANIFESTO.md` to clarify the architectural principles for future tasks."

[REQUIRED FORMAT]
Generate ONLY a single text string containing the NEXT STRATEGIC OBJECTIVE. Be concise, but specific enough to be actionable.
"""
    # Note: The original code directly assigned this template to `prompt`.
    # Here, we return it so it can be assigned to `prompt` in the calling function.
    return meta_analysis_prompt_template


def build_standard_objective_prompt(
    memory_context_section: str,
    performance_summary_str: str,
    code_analysis_summary_str: str,
    current_manifest: str,
    capabilities_content: str,
    roadmap_content: str
) -> str:
    """
    Constrói o prompt padrão para gerar o próximo objetivo estratégico.
    """
    prompt_template = """
[Main Context]
You are the 'Planejador Estratégico Avançado' do agente autônomo Hephaestus. Sua principal responsabilidade é identificar e propor o próximo objetivo de desenvolvimento mais impactante para a evolução do agente ou do projeto em análise.

[Decision Process for the Next Objective]
1.  **Analyze Performance:** Review the `[PERFORMANCE ANALYSIS]` section.
2.  **Analyze Code Metrics:** Review the `[CODE METRICS AND ANALYSIS]` section.
3.  **Consider Strategic Documents:** Review `[CAPABILITIES DOCUMENT]` and `[ROADMAP DOCUMENT]` to understand current capabilities, desired future states, and strategic direction. Identify gaps or next steps.
4.  **Consider the Project Manifest:** If the `[CURRENT PROJECT MANIFEST]` is provided, use it for context.
5.  **Review Recent History:** The `[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]` section provides context.
6.  **Prioritize RSI:** Focus on objectives that enhance the agent's ability to self-improve, improve its core logic, prompts, or strategies.
7.  **Prioritize Capabilities & Roadmap:** Generate objectives that fill gaps in `[CAPABILITIES DOCUMENT]` or advance items in `[ROADMAP DOCUMENT]`.
8.  **Prioritize Structural and Quality Improvements:** Based on metrics and strategic documents.
9.  **Be Specific and Actionable:** The objective should be clear, concise, and indicate a concrete action.

1.  **Analyze Performance:** Review the `[PERFORMANCE ANALYSIS]` section to understand the agent's overall success rate and identify trends, especially focusing on strategies with high failure rates.
2.  **Analyze Code Metrics:** Review the `[CODE METRICS AND ANALYSIS]` section below. It contains data on file size (LOC), function size (LOC), cyclomatic complexity (CC) of functions, and modules that may be missing tests.
3.  **Consider the Project Manifest:** If the `[CURRENT PROJECT MANIFEST]` is provided, use it to understand the overall goals, architecture, and areas already documented or needing attention.
4.  **Review Recent History:** The `[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]` section provides context on recent tasks, successes, and failures. Avoid repeating objectives that recently failed in the same way, unless the cause of failure has been resolved. Use history to build on successes.
5.  **Prioritize Structural and Quality Improvements:** Based on metrics, identify opportunities to:
    *   Refactor very large modules or very long/complex functions.
    *   Create tests for critical/complex modules or functions that lack them.
    *   Improve documentation (docstrings, manifest) where crucial.
    *   Propose the creation of new capabilities (new agents, tools) if the analysis indicates a strategic need.
6.  **Prioritize Prompt and Strategy Optimization (RSI Focus):** If the performance analysis reveals strategies with consistently low success rates, consider objectives to:
    *   Refine the prompts used by agents (e.g., Architect, Maestro, ErrorAnalysis) for those failing strategies.
    *   Propose new or modified validation strategies in `hephaestus_config.json` to address specific failure patterns.
7.  **Be Specific and Actionable:** The objective should be clear, concise, and indicate a concrete action.

{memory_section}

[PERFORMANCE ANALYSIS]
{performance_summary}

[CODE METRICS AND ANALYSIS]
{code_analysis_summary}

[CAPABILITIES DOCUMENT (CAPABILITIES.md)]
{capabilities_content}

[ROADMAP DOCUMENT (ROADMAP.md)]
{roadmap_content}


[CURRENT PROJECT MANIFEST (if existing)]
{current_manifest}

[Examples of Smart and Self-Aware Objectives]
*   **Performance-Based Objectives:**
    *   "The agent's success rate is low. Analyze the `evolution_log.csv` to identify the most common causes of failure and propose a solution."
    *   "Given the high number of failed cycles, implement a more robust error analysis mechanism in `error_analyzer.py`."
*   **Prompt/Strategy Optimization Objectives (RSI Focus):**
    *   "The 'SYNTAX_ONLY' strategy has a high failure rate. Analyze the prompts used by the ArchitectAgent when this strategy is chosen and propose modifications to improve syntax correctness."
    *   "Propose a new validation strategy in `hephaestus_config.json` called 'ADVANCED_LINTING' that includes `ruff` checks before applying patches, to reduce syntax errors."
    *   "Analyze the `MaestroAgent`'s decision-making process for objectives related to documentation updates, as the 'DOC_UPDATE_STRATEGY' has a low success rate. Refine its prompt to improve accuracy."
*   **Metrics-Based Refactoring:**
    *   "Refactor the module `agent/brain.py` (LOC: 350) which is extensive, considering splitting responsibilities into smaller modules (e.g., `agent/prompt_builder.py` or `agent/analysis_processor.py`)."
    *   "The function `generate_next_objective` in `agent/brain.py` (LOC: 85, CC: 12) is long and complex. Propose a plan to refactor it into smaller, more focused functions."
    *   "Analyze the most complex functions (CC > 10) listed in the metrics and select one for refactoring."
*   **Test Creation (Generate New Test Files):**
    *   "The module `agent/project_scanner.py` is missing a test file. Create a new test file `tests/agent/test_project_scanner.py` with basic unit tests for the `analyze_code_metrics` function."
    *   "Module `agent/memory.py` lacks tests. Generate `tests/agent/test_memory.py` and include placeholder tests for its public functions."
    *   "Create unit tests for the module `agent/tool_executor.py` in a new file `tests/agent/test_tool_executor.py`, focusing on the `web_search` function."
    *   "The function `call_llm_api` in `agent/utils/llm_client.py` is critical. Ensure robust unit tests exist for it in `tests/agent/utils/test_llm_client.py`, covering success and failure cases. If the test file doesn't exist, create it."
*   **Test-Driven Development (TDD) Flow:**
    *   "The previous cycle successfully created a new test file `tests/agent/test_new_feature.py` which is now failing as expected. The next objective is to implement the minimal code in `agent/new_feature.py` required to make the tests in `tests/agent/test_new_feature.py` pass."
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
    return prompt_template.format(
        memory_section=memory_context_section,
        performance_summary=performance_summary_str,
        code_analysis_summary=code_analysis_summary_str,
        current_manifest=current_manifest if current_manifest.strip() else "N/A (Manifesto non-existent or empty)",
        capabilities_content=capabilities_content,
        roadmap_content=roadmap_content
    )
