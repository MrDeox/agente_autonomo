import logging
from typing import Dict, Any, Optional, List
import os

from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response

class LogAnalysisAgent:
    """
    An agent specialized in analyzing log files to identify issues and suggest improvements.
    """
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger

    def analyze_logs(self, log_file_path: str, lines_to_analyze: int = 200) -> Optional[Dict[str, Any]]:
        """
        Reads the tail of a log file and uses an LLM to analyze its content.

        Args:
            log_file_path: The path to the log file.
            lines_to_analyze: The number of recent lines to analyze.

        Returns:
            A dictionary with the analysis results or None if an error occurs.
        """
        self.logger.info(f"Analyzing last {lines_to_analyze} lines of '{log_file_path}'...")
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            
            recent_lines = log_lines[-lines_to_analyze:]
            if not recent_lines:
                self.logger.warning(f"Log file '{log_file_path}' is empty or has fewer than {lines_to_analyze} lines. Nothing to analyze.")
                return {"summary": "Log file is empty.", "issues": [], "suggested_objective": None}
            
            log_content = "".join(recent_lines)

            prompt = self._build_analysis_prompt(log_content)

            raw_response, error = call_llm_api(
                model_config=self.model_config,
                prompt=prompt,
                temperature=0.2,
                logger=self.logger
            )

            if error:
                self.logger.error(f"LogAnalysisAgent: LLM call failed: {error}")
                return None

            if not raw_response:
                self.logger.error("LogAnalysisAgent: Received empty response from LLM.")
                return None

            parsed_response, parse_error = parse_json_response(raw_response, self.logger)

            if parse_error or not isinstance(parsed_response, dict):
                self.logger.error(f"LogAnalysisAgent: Failed to parse LLM response: {parse_error or 'Invalid format'}")
                return None

            self.logger.info(f"Log analysis complete. Found {len(parsed_response.get('issues', []))} potential issues.")
            return parsed_response

        except FileNotFoundError:
            self.logger.error(f"Log file not found: {log_file_path}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during log analysis: {e}", exc_info=True)
            return None

    def _build_analysis_prompt(self, log_content: str) -> str:
        """Builds the prompt for the LLM to analyze log content."""
        return f"""
[IDENTITY]
You are an expert Site Reliability Engineer (SRE). Your task is to analyze the following log snippets to identify potential problems, recurring errors, or opportunities for system improvement.

[LOG CONTENT]
```
{log_content}
```

[ANALYSIS TASK]
Carefully review the logs and perform the following actions:
1.  **Identify Patterns:** Look for repeated WARNINGS, ERRORS, or stack traces.
2.  **Correlate Events:** See if certain informational messages precede errors.
3.  **Suggest Action:** Based on your analysis, determine if an action is required. This could be a bug fix, a configuration change, or a performance improvement.

[OUTPUT FORMAT]
Your response MUST be a valid JSON object with the following structure:
{{
  "summary": "A brief, one-sentence summary of the log's health.",
  "issues": [
    {{
      "type": "ERROR" | "WARNING" | "PERFORMANCE" | "INFO",
      "description": "A detailed description of the identified issue.",
      "count": "The number of times this issue appeared in the snippet."
    }}
  ],
  "suggested_objective": "If any significant issues are found, propose a clear, actionable objective for the Hephaestus agent to resolve the root cause. If no action is needed, this should be null."
}}

Example for a FAILED review:
{{
  "summary": "The logs show repeated `TypeError` exceptions during the agent's main run loop.",
  "issues": [
    {{
      "type": "ERROR",
      "description": "NameError: name 'CycleRunner' is not defined in tools/app.py.",
      "count": 1
    }}
  ],
  "suggested_objective": "[BUGFIX] The `worker_thread` in `tools/app.py` is failing with a `NameError` because `CycleRunner` is not imported. Add the necessary import statement to fix the application startup."
}}

Example for a HEALTHY review:
{{
  "summary": "Logs indicate normal operation with successful meta-cognitive cycles and no critical errors.",
  "issues": [],
  "suggested_objective": null
}}
""" 