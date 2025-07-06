"""
The agent package contains all the core logic for the Hephaestus autonomous agent.
"""

# This file is intentionally kept lightweight.
# Submodules should be imported directly by the components that need them
# to avoid circular dependencies and improve clarity.

# __init__.py for the agent package

from .agents import ErrorAnalysisAgent
from .agents import ArchitectAgent, MaestroAgent
# ErrorCorrectionAgent and PerformanceAnalysisAgent are not directly exported here,
# but are available via from agent.agents import ...
from .brain import generate_next_objective, generate_capacitation_objective, generate_commit_message
from .code_validator import validate_python_code, validate_json_syntax, perform_deep_validation
# A importação de run_cycles foi removida, pois a lógica agora é contida dentro de HephaestusAgent e CycleRunner
# from .cycle_runner import run_cycles
from .code_metrics import analyze_complexity, detect_code_duplication, calculate_quality_score # Updated import
from .git_utils import initialize_git_repository
from .memory import Memory
from .patch_applicator import apply_patches
from .project_scanner import update_project_manifest, analyze_code_metrics
from .state import AgentState
from .tool_executor import run_pytest, check_file_existence, run_in_sandbox, run_git_command

# Exportações principais (se necessário)
__all__ = [
    "update_project_manifest",
    "generate_next_objective",
    "generate_commit_message",
    "run_pytest",
    "apply_patches",
]
