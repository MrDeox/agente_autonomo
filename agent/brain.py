from typing import Optional, Any, Dict
import logging

from agent.objective_generator import generate_next_objective, generate_capacitation_objective
from agent.commit_message_generator import generate_commit_message

# The brain module now serves as a facade/coordinator between the specialized modules
__all__ = ['generate_next_objective', 'generate_capacitation_objective', 'generate_commit_message']