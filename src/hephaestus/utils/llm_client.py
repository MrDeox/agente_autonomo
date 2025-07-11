import os
import json
import logging
import requests
import traceback
from typing import Optional, Tuple, Dict, Any
import google.generativeai as genai
import httpx
import asyncio

# Import our new API Key Manager
try:
    from .api_key_manager import get_api_key_manager
    API_KEY_MANAGER_AVAILABLE = True
except ImportError:
    API_KEY_MANAGER_AVAILABLE = False
    logging.warning("API Key Manager not available, falling back to single key mode")

# Configure Gemini client (fallback mode)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Constants
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def call_gemini_api_with_key(api_key: str, model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls the Google Gemini API with a specific key.
    """
    logger.info(f"Attempting to call Gemini API with model: {model}")
    try:
        # Configure client with specific key
        genai.configure(api_key=api_key)
        
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

def call_gemini_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls the Google Gemini API with automatic key management.
    """
    if API_KEY_MANAGER_AVAILABLE:
        manager = get_api_key_manager()
        key = manager.get_best_key("gemini")
        
        if key:
            result, error = call_gemini_api_with_key(key.key, model, prompt, temperature, max_tokens, logger)
            
            # Mark result in key manager
            success = result is not None
            manager.mark_key_result(key, success, error or "")
            
            if success:
                return result, error
            else:
                # Try fallback if this key failed
                logger.warning(f"Key {key.name} failed, trying fallback...")
                fallback_key, provider = manager.get_key_with_fallback("gemini")
                if fallback_key and provider == "gemini":
                    result, error = call_gemini_api_with_key(fallback_key.key, model, prompt, temperature, max_tokens, logger)
                    manager.mark_key_result(fallback_key, result is not None, error or "")
                    return result, error
        
        return None, "No available Gemini API keys"
    
    # Fallback to single key mode
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

def call_openrouter_api_with_key(api_key: str, model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls OpenRouter API with a specific key.
    """
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

def call_openrouter_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls OpenRouter API with automatic key management.
    """
    if API_KEY_MANAGER_AVAILABLE:
        manager = get_api_key_manager()
        key = manager.get_best_key("openrouter")
        
        if key:
            result, error = call_openrouter_api_with_key(key.key, model, prompt, temperature, max_tokens, logger)
            
            # Mark result in key manager
            success = result is not None
            manager.mark_key_result(key, success, error or "")
            
            if success:
                return result, error
            else:
                # Try fallback if this key failed
                logger.warning(f"Key {key.name} failed, trying fallback...")
                fallback_key, provider = manager.get_key_with_fallback("openrouter")
                if fallback_key and provider == "openrouter":
                    result, error = call_openrouter_api_with_key(fallback_key.key, model, prompt, temperature, max_tokens, logger)
                    manager.mark_key_result(fallback_key, result is not None, error or "")
                    return result, error
        
        return None, "No available OpenRouter API keys"
    
    # Fallback to single key mode
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None, "OPENROUTER_API_KEY environment variable not set."

    return call_openrouter_api_with_key(api_key, model, prompt, temperature, max_tokens, logger)

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

async def call_openrouter_api_async(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Async version of OpenRouter API call.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None, "OPENROUTER_API_KEY environment variable not set."

    logger.info(f"[async] Attempting to call OpenRouter API with model: {model}")
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
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            response_json = response.json()

        logger.debug(f"[async] OpenRouter API Response: {json.dumps(response_json, indent=2)}")

        content = response_json.get("choices", [{}])[0].get("message", {}).get("content")
        if content is not None:
            return content, None
        else:
            err_msg = "API response missing or has invalid structure."
            logger.error(f"{err_msg} Full response: {response_json}")
            return None, f"{err_msg} Full response: {response_json}"

    except httpx.HTTPStatusError as http_err:
        error_details = f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}, Response: {http_err.response.text}"
        logger.error(error_details)
        return None, error_details
    except Exception as e:
        error_details = f"Unexpected error during OpenRouter API call: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_details)
        return None, error_details

async def call_gemini_api_async(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Async version of Gemini API call (runs in thread pool since google.generativeai is sync).
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, call_gemini_api, model, prompt, temperature, max_tokens, logger)

async def call_llm_with_fallback_async(model_config: dict, prompt: str, temperature: float, logger: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Async version of LLM call with fallback.
    """
    if isinstance(model_config, str):
        model_config = {"primary": model_config}

    primary_model = model_config.get("primary")
    fallback_model = model_config.get("fallback")
    max_tokens = model_config.get("max_tokens")

    # Try primary model first
    if primary_model:
        logger.info(f"[async] Calling primary model: {primary_model}")
        content, error = None, None
        if primary_model.startswith("gemini/"):
            content, error = await call_gemini_api_async(primary_model, prompt, temperature, max_tokens, logger)
        else:
            content, error = await call_openrouter_api_async(primary_model, prompt, temperature, max_tokens, logger)

        if content is not None:
            return content, None
        logger.warning(f"[async] Primary model '{primary_model}' failed. Error: {error}. Trying fallback.")

    # If primary fails or is not defined, try fallback
    if fallback_model:
        logger.info(f"[async] Calling fallback model: {fallback_model}")
        return await call_openrouter_api_async(fallback_model, prompt, temperature, max_tokens, logger)

    return None, "Both primary and fallback models failed or are not configured."

# Alias para uso externo
call_llm_api_async = call_llm_with_fallback_async
