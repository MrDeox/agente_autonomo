import logging
from typing import Dict, Any, Optional

from agent.utils.llm_client import call_llm_api

class ModelSommelierAgent:
    """
    An agent that analyzes the performance of other agents and proposes
    optimizations to their underlying LLM configurations.
    """
    def __init__(self, model_config: Dict[str, Any], config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger

    def propose_model_optimization(self, agent_performance_summary: Dict[str, Any], available_models: list[str]) -> Optional[str]:
        """
        Analyzes agent performance and proposes a model change objective.

        Args:
            agent_performance_summary: A summary of each agent's performance.
            available_models: A list of currently available free models.

        Returns:
            A string containing a single, actionable objective, or None if no
            optimization is deemed necessary.
        """
        self.logger.info("🍷 Model Sommelier: Analyzing agent performance for model optimization...")

        if not agent_performance_summary:
            self.logger.warning("Model Sommelier: No agent performance data to analyze.")
            return None

        # Convert data to string for the prompt
        perf_summary_str = "\\n".join([f"- {agent}: {stats}" for agent, stats in agent_performance_summary.items()])
        models_str = ", ".join(available_models)

        prompt = self._build_optimization_prompt(perf_summary_str, models_str)
        
        objective, error = call_llm_api(
            model_config=self.model_config,
            prompt=prompt,
            temperature=0.4, # A bit more creative to find novel solutions
            logger=self.logger
        )

        if error:
            self.logger.error(f"Model Sommelier: LLM call failed: {error}")
            return None
        
        if not objective or "No optimization needed" in objective:
            self.logger.info("Model Sommelier: No model optimization proposed at this time.")
            return None

        self.logger.info(f"Model Sommelier: Proposing new optimization objective: {objective.strip()}")
        return objective.strip()

    def _build_optimization_prompt(self, performance_summary: str, available_models: str) -> str:
        """Builds the prompt for the LLM to decide on a model optimization."""
        return f"""
[IDENTITY]
You are the "Model Sommelier," an expert AI system that optimizes the Hephaestus agent swarm. Your task is to analyze the performance of each agent and determine if changing its underlying language model would improve results.

[CONTEXT]
You have access to real-time performance data for each agent and a list of currently available free models from the OpenRouter API.

[AGENT PERFORMANCE SUMMARY]
This data shows each agent's success rate and average quality score.
{performance_summary}

[AVAILABLE FREE MODELS]
{available_models}

[YOUR TASK]
1.  **Identify the Weakest Link:** Find the agent with the lowest success rate or quality score. This is your primary target for optimization.
2.  **Hypothesize a Better Model:** Look at the list of available models. Propose changing the target agent's primary model to a DIFFERENT one from the list that might be better suited for its task (e.g., if a small model is failing on a complex task like code review, suggest a larger one. If a simple task is using a slow, large model, suggest a smaller one).
3.  **Generate a Configuration Change Objective:** Create a clear, actionable objective for the main Hephaestus agent to execute. The objective MUST be to modify the `config/models/main.yaml` file.

[Example Objectives]
- "[MODEL_OPTIMIZATION] The 'CodeReviewAgent' has a low success rate. Change its primary model in `config/models/main.yaml` to 'mistralai/mistral-7b-instruct:free' to improve its analytical capabilities."
- "[MODEL_OPTIMIZATION] The 'LogAnalysisAgent' is using a powerful model unnecessarily. Change its primary model in `config/models/main.yaml` to 'qwen/qwen3-0.6b-04-28:free' to improve efficiency."
- "No optimization needed at this time." (If performance is acceptable across all agents).

[OUTPUT FORMAT]
Respond ONLY with the text string of the single, most impactful objective, or "No optimization needed at this time."
""" 