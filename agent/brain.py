from typing import Optional, Any, Dict
import logging
import os

from agent.objective_generator import generate_next_objective, generate_capacitation_objective
from agent.commit_message_generator import generate_commit_message

# The brain module now serves as a facade/coordinator between the specialized modules
__all__ = ['generate_next_objective', 'generate_capacitation_objective', 'generate_commit_message']

def generate_next_objective(
    model_config: Dict[str, str],
    current_manifest: str,
    current_objective: Optional[str] = None
) -> str:
    """
    Generates the next evolutionary objective using code analysis and performance data.
    """
    logger = logging.getLogger(__name__)

    # Read dashboard content for context
    dashboard_content = ""
    try:
        dashboard_path = "templates/dashboard.html"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, "r", encoding="utf-8") as f:
                dashboard_content = f.read()
            if logger: logger.info("templates/dashboard.html read successfully for context.")
    except Exception as e:
        if logger: logger.warning(f"Could not read dashboard.html: {e}")

    # 2. Analyze performance from ModelOptimizer
    performance_summary_str = ""
    if model_optimizer:
        memory_context_section = build_memory_context_section(memory.get_full_history_for_prompt())

    # 4. Build the prompt using functions from prompt_builder
    prompt: str
    if model_optimizer:
        prompt = build_standard_objective_prompt(
            memory_context_section=memory_context_section,
            performance_summary_str=performance_summary_str,
            code_analysis_summary_str=code_analysis_summary_str,
            current_manifest=current_manifest,
            capabilities_content=capabilities_content,
            roadmap_content=roadmap_content,
            dashboard_content=dashboard_content
        )

    if logger: logger.debug(f"Prompt for generate_next_objective:\\n{prompt}")

    # 4. Call LLM API using the centralized function
    # ... existing code ...

    return prompt