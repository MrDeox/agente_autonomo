import os
import json
import logging
import requests
import traceback
from typing import Optional, Tuple, Dict, Any
import google.generativeai as genai

# Configure Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Constants
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # Load JIT inside the function
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def call_gemini_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls the Google Gemini API.
    """
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY environment variable not set."
    
    logger.info(f"Attempting to call Gemini API with model: {model}")
    try:
        # Model name in config is "gemini/model-name", we need to pass "model-name"
        model_name = model.split('/')[-1]
        gemini_model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        if max_tokens and max_tokens > 0:
            generation_config.max_output_tokens = max_tokens

        response = gemini_model.generate_content(prompt, generation_config=generation_config)
        
        if response.text:
            logger.debug(f"Gemini API Response: {response.text}")
            return response.text, None
        else:
            # Handle cases where the response might be blocked or empty
            error_message = "Gemini API call failed: No text in response."
            if response.prompt_feedback:
                error_message += f" Prompt Feedback: {response.prompt_feedback}"
            logger.error(error_message)
            return None, error_message

    except Exception as e:
        error_details = f"Unexpected error during Gemini API call: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_details)
        return None, error_details

def call_openrouter_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls a generic OpenAI-compatible API (like OpenRouter).
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None, "OPENROUTER_API_KEY environment variable not set."

    logger.info(f"Attempting to call OpenRouter API with model: {model}")
    url = f"{OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    if max_tokens and max_tokens > 0:
        payload['max_tokens'] = max_tokens

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()

        logger.debug(f"OpenRouter API Response: {json.dumps(response_json, indent=2)}")

        content = response_json.get("choices", [{}])[0].get("message", {}).get("content")
        if content is not None:
            return content, None
        else:
            err_msg = "API response missing or has invalid structure."
            logger.error(f"{err_msg} Full response: {response_json}")
            return None, f"{err_msg} Full response: {response_json}"

    except requests.exceptions.HTTPError as http_err:
        error_details = f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}, Response: {http_err.response.text}"
        logger.error(error_details)
        return None, error_details
    except Exception as e:
        error_details = f"Unexpected error during OpenRouter API call: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_details)
        return None, error_details

def call_llm_with_fallback(model_config: dict, prompt: str, temperature: float, logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Orchestrates LLM calls with a primary and fallback model.
    """
    # Permitir que model_config seja string ou dict
    if isinstance(model_config, str):
        model_config = {"primary": model_config}

    primary_model = model_config.get("primary")
    fallback_model = model_config.get("fallback")
    max_tokens = model_config.get("max_tokens")

    # Try primary model first
    if primary_model:
        logger.info(f"Calling primary model: {primary_model}")
        content, error = None, None
        if primary_model.startswith("gemini/"):
            content, error = call_gemini_api(primary_model, prompt, temperature, max_tokens, logger)
        else: # Assuming other primary models are OpenAI compatible
            content, error = call_openrouter_api(primary_model, prompt, temperature, max_tokens, logger)

        if content is not None:
            return content, None
        
        logger.warning(f"Primary model '{primary_model}' failed. Error: {error}. Trying fallback.")

    # If primary fails or is not defined, try fallback
    if fallback_model:
        logger.info(f"Calling fallback model: {fallback_model}")
        # Assuming all fallbacks are OpenAI compatible for now
        return call_openrouter_api(fallback_model, prompt, temperature, max_tokens, logger)

    return None, "Both primary and fallback models failed or are not configured."

# For backward compatibility, you can alias the old function name
call_llm_api = call_llm_with_fallback
