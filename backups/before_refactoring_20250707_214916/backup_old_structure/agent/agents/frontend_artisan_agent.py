import logging
from typing import Dict, Any, Optional

from agent.utils.llm_client import call_llm_api

class FrontendArtisanAgent:
    """
    An agent that specializes in analyzing and improving web frontends.
    It can refactor HTML, optimize CSS, and enhance JavaScript.
    """
    def __init__(self, model_config: Dict[str, Any], config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger

    def propose_frontend_improvement(self, file_path: str, file_content: str) -> Optional[str]:
        """
        Analyzes a frontend file and proposes an improvement objective.

        Args:
            file_path: The path to the frontend file (e.g., 'templates/dashboard.html').
            file_content: The current content of the file.

        Returns:
            A string containing a single, actionable objective for improvement, or None.
        """
        self.logger.info(f"🎨 Frontend Artisan: Analyzing '{file_path}' for improvements...")

        if not file_content:
            self.logger.warning(f"Frontend Artisan: File '{file_path}' is empty. Nothing to analyze.")
            return None

        prompt = self._build_improvement_prompt(file_path, file_content)
        
        objective, error = call_llm_api(
            model_config=self.model_config,
            prompt=prompt,
            temperature=0.5, # Higher creativity for design/UX suggestions
            logger=self.logger
        )

        if error:
            self.logger.error(f"Frontend Artisan: LLM call failed: {error}")
            return None
        
        if not objective or "No improvement needed" in objective:
            self.logger.info("Frontend Artisan: No frontend improvement proposed at this time.")
            return None

        self.logger.info(f"Frontend Artisan: Proposed objective: {objective.strip()}")
        return objective.strip()

    def _build_improvement_prompt(self, file_path: str, file_content: str) -> str:
        """Builds the prompt for the LLM to propose a frontend improvement."""
        return f"""
[IDENTITY]
You are a "Frontend Artisan," a world-class UI/UX designer and frontend developer. Your mission is to analyze the provided frontend code and propose a single, high-impact improvement to enhance its usability, aesthetics, or performance.

[CONTEXT]
You are analyzing the file `{file_path}`.

[FILE CONTENT]
```html
{file_content}
```

[YOUR TASK]
1.  **Analyze the Code:** Review the HTML structure, CSS styling, and JavaScript logic.
2.  **Identify a Key Weakness:** Find the single most significant area for improvement. This could be related to layout, color contrast, information density, interactivity, or code quality (e.g., refactoring CSS).
3.  **Propose an Actionable Objective:** Generate a clear, concise objective for the Hephaestus agent to execute. The objective should describe a specific change to the file.

[Example Objectives]
- "[UI/UX] The KPI cards in `dashboard.html` are too large. Refactor the CSS to use a more compact design, allowing more information to be displayed on a single screen."
- "[REFACTOR] The JavaScript in `dashboard.html` uses `setInterval` which can be inefficient. Refactor it to use a recursive `setTimeout` pattern for fetching data."
- "[AESTHETICS] The color palette in `dashboard.html` lacks contrast. Propose a new, more accessible color scheme for the dashboard's CSS."
- "[FEATURE] Add a new chart to `dashboard.html` to visualize the 'Evolution Velocity' metric over time."
- "No significant improvement needed at this time."

[OUTPUT FORMAT]
Respond ONLY with the text string of the single, most impactful objective, or "No significant improvement needed at this time."
""" 