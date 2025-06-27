import json
import logging # Changed from 'Any' to 'logging' for proper type hinting
import requests
import traceback # Kept for now, as it was in one of the versions
from typing import Optional, Tuple, Any # 'Any' can be replaced if logger type is more specific

# Common function to call LLM API
# Taken from agent/agents.py as it seemed slightly more complete (e.g., no traceback import)
# but added back traceback for safety if it was used in specific error conditions.
def call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Helper function to make calls to the LLM API.

    Args:
        api_key: The API key for authentication.
        model: The model to use for the completion.
        prompt: The prompt to send to the model.
        temperature: The temperature for sampling.
        base_url: The base URL for the API.
        logger: Logger instance for logging.

    Returns:
        A tuple containing the content of the response (or None if an error occurred)
        and an error message (or None if successful).
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        response_json = response.json()

        if logger:
            logger.debug(f"LLM API Response: {json.dumps(response_json, indent=2)}")

        if "choices" not in response_json or not response_json["choices"]:
            err_msg = "API response missing 'choices' key or 'choices' is empty."
            if logger:
                logger.error(f"{err_msg} Full response: {response_json}")
            return None, f"{err_msg} Full response: {response_json}"

        # Check if message and content are present
        message = response_json["choices"][0].get("message")
        if not message:
            err_msg = "API response 'choices'[0] missing 'message' key."
            if logger:
                logger.error(f"{err_msg} Full response: {response_json}")
            return None, f"{err_msg} Full response: {response_json}"

        content = message.get("content")
        if content is None: # content can be an empty string, which is valid
            err_msg = "API response 'message' missing 'content' key."
            if logger:
                logger.error(f"{err_msg} Full response: {response_json}")
            return None, f"{err_msg} Full response: {response_json}"

        return content, None
    except requests.exceptions.HTTPError as http_err:
        error_details = f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}, Response: {http_err.response.text}"
        if logger:
            logger.error(error_details)
        return None, error_details
    except requests.exceptions.RequestException as req_err:
        error_details = f"Request failed: {req_err}"
        if logger:
            logger.error(error_details)
        return None, error_details
    except KeyError as key_err:
        error_details = f"KeyError: {str(key_err)} in API response. This might indicate an unexpected response structure."
        if logger:
            logger.error(f"{error_details} Full response: {response_json}")
        return None, error_details
    except Exception as e:
        # Using traceback here to get more details on unexpected errors
        error_details = f"Unexpected error during LLM API call: {str(e)}\n{traceback.format_exc()}"
        if logger:
            logger.error(error_details)
        return None, error_details
