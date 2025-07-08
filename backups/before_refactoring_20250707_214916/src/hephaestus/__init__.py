"""
Hephaestus: Recursive Self-Improvement Agent

Um agente autônomo focado em aprimoramento recursivo de suas próprias capacidades.
"""

__version__ = "0.1.0"
__author__ = "MrDeox"

from .core.agent import HephaestusAgent
from .core.brain import generate_next_objective
from .core.memory import Memory

__all__ = [
    "HephaestusAgent",
    "generate_next_objective", 
    "Memory",
]