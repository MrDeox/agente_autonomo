import json
import logging
import traceback
from typing import Optional, Tuple

import aiohttp
import asyncio # Added for timeout
from cachetools import LFUCache

# Simple in-memory cache for LLM responses
# Cache up to 128 entries, with LFU replacement policy
llm_cache = LFUCache(maxsize=128)
# You might want to make cache configuration (size, TTL) part of hephaestus_config.json

async def call_llm_api(
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
    base_url: str,
    logger: logging.Logger,
    timeout_seconds: int = 60,  # Default timeout for the API call
    use_cache: bool = True # Flag to control caching
) -> Tuple[Optional[str], Optional[str]]:
    """
    Helper function to make calls to the LLM API asynchronously.
    Includes caching and timeout.
    """
    cache_key = None
    if use_cache:
        # Create a cache key based on relevant parameters
        # Hashing the prompt can be good if it's very long
        # For simplicity, using a tuple of model, prompt (or its hash), and temperature
        try:
            prompt_hash = str(hash(prompt)) # Simple hash
        except Exception: # pragma: no cover
            prompt_hash = prompt # Fallback if hashing fails for some reason
        cache_key = (model, prompt_hash, temperature, base_url)
        if cache_key in llm_cache:
            if logger:
                logger.info(f"Returning cached response for model {model}, prompt hash {prompt_hash}")
            return llm_cache[cache_key]

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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout_seconds)
            ) as response:
                response_text = await response.text() # Read text first for better error reporting
                response.raise_for_status()  # Raises an ClientResponseError for bad responses (4XX or 5XX)

                try:
                    response_json = json.loads(response_text)
                except json.JSONDecodeError as json_err:
                    err_msg = f"JSON decode error: {json_err}. Response text: {response_text[:500]}"
                    if logger: logger.error(err_msg)
                    return None, err_msg

                if logger:
                    logger.debug(f"LLM API Response: {json.dumps(response_json, indent=2)}")

                if "choices" not in response_json or not response_json["choices"]:
                    err_msg = "API response missing 'choices' key or 'choices' is empty."
                    # Avoid logging full response_json if it's huge or sensitive without redaction
                    if logger: logger.error(f"{err_msg} Response keys: {list(response_json.keys())}")
                    return None, err_msg

                message = response_json["choices"][0].get("message")
                if not message:
                    err_msg = "API response 'choices'[0] missing 'message' key."
                    if logger: logger.error(err_msg)
                    return None, err_msg

                content = message.get("content")
                if content is None:
                    err_msg = "API response 'message' missing 'content' key."
                    if logger: logger.error(err_msg)
                    return None, err_msg

                if use_cache and cache_key:
                    llm_cache[cache_key] = (content, None)

                return content, None

    except aiohttp.ClientResponseError as http_err:
        # response_text might already be defined if status check passed initially but something else failed
        # For raise_for_status, response_text is available via http_err.message if not read before
        # However, reading it before raise_for_status is safer for detailed logging.
        error_details = f"HTTP error occurred: {http_err.status} {http_err.message}. Response: {response_text[:500]}"
        if logger: logger.error(error_details)
        return None, error_details
    except asyncio.TimeoutError:
        error_details = f"API call timed out after {timeout_seconds} seconds for model {model} at {url}"
        if logger: logger.error(error_details)
        return None, error_details
    except aiohttp.ClientError as client_err: # Catches other aiohttp client errors (e.g., connection errors)
        error_details = f"AIOHTTP client error: {client_err}"
        if logger: logger.error(error_details)
        return None, error_details
    except KeyError as key_err: # Should be less likely with .get() usage but good as a safeguard
        # response_json might not be defined if error is early
        err_response_text = "response_json not available"
        try:
            err_response_text = json.dumps(response_json) if 'response_json' in locals() else response_text
        except Exception: pass # pragma: no cover
        error_details = f"KeyError: {str(key_err)} in API response. Response (partial): {err_response_text[:500]}"
        if logger: logger.error(error_details)
        return None, error_details
    except Exception as e: # General catch-all
        error_details = f"Unexpected error during LLM API call: {str(e)}\n{traceback.format_exc()}"
        if logger: logger.error(error_details)
        return None, error_details
