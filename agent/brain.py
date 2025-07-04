from typing import Optional, Any, Dict
import logging
import os

from agent.objective_generator import generate_capacitation_objective
from agent.commit_message_generator import generate_commit_message

# The brain module now serves as a facade/coordinator between the specialized modules
__all__ = ['generate_next_objective', 'generate_capacitation_objective', 'generate_commit_message']

def generate_next_objective(
    model_config: Dict[str, str],
    current_manifest: str,
    current_objective: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    project_root_dir: str = ".",
    memory: Optional[Any] = None,
    model_optimizer: Optional[Any] = None
) -> str:
    """
    Generates the next evolutionary objective using code analysis and performance data.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # Read dashboard content for context
    dashboard_content = ""
    try:
        dashboard_path = "templates/dashboard.html"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, "r", encoding="utf-8") as f:
                dashboard_content = f.read()
            logger.info("templates/dashboard.html read successfully for context.")
    except Exception as e:
        logger.warning(f"Could not read dashboard.html: {e}")

    # Simplified implementation - delegate to objective_generator
    from agent.objective_generator import generate_next_objective as _generate_next_objective
    
    try:
        result = _generate_next_objective(
            model_config=model_config,
            current_manifest=current_manifest,
            logger=logger,
            project_root_dir=project_root_dir,
            config=None,
            memory=memory,
            model_optimizer=model_optimizer,
            current_objective=current_objective
        )
        return result
    except Exception as e:
        logger.error(f"Error generating next objective: {e}")
        return "Analisar e melhorar a arquitetura do sistema"