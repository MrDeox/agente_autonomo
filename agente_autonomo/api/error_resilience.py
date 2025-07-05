"""
Sistema de Resiliência a Erros para o Servidor MCP Hephaestus
============================================================

Este módulo fornece funcionalidades robustas para tratamento de erros,
validação de dados e recuperação de falhas no servidor MCP.
"""

import json
import logging
import traceback
from typing import Any, Dict, Optional, Union, Callable
from datetime import datetime
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class SelfReflectionRequest(BaseModel):
    """Modelo Pydantic para validação de requisições de auto-reflexão"""
    focus_area: str = Field(default="general", min_length=1, max_length=100)
    
    @validator('focus_area')
    def validate_focus_area(cls, v):
        """Validação adicional para área de foco"""
        if v.strip() == "":
            raise ValueError("Focus area cannot be empty")
        return v

class AwarenessMetric(BaseModel):
    """Modelo para métricas de auto-consciência"""
    meta_awareness_score: float = Field(default=0.0, ge=0, le=1)
    temporal_awareness: float = Field(default=0.0, ge=0, le=1)
    introspection_depth: float = Field(default=0.0, ge=0, le=1)
    cognitive_coherence: float = Field(default=0.0, ge=0, le=1)
    self_knowledge_confidence: float = Field(default=0.0, ge=0, le=1)

class CognitiveState(BaseModel):
    """Modelo para estado cognitivo"""
    intelligence_level: float = Field(default=0.0, ge=0, le=1)
    self_awareness_score: float = Field(default=0.0, ge=0, le=1)
    creativity_index: float = Field(default=0.0, ge=0, le=1)
    adaptation_rate: float = Field(default=0.0, ge=0, le=1)
    system_stress: float = Field(default=0.0, ge=0, le=1)

class SelfAwarenessResponse(BaseModel):
    """Modelo para respostas de auto-consciência"""
    meta_awareness: float = Field(default=0.0, ge=0, le=1)
    new_insights: list = Field(default_factory=list)
    self_narrative: Dict[str, str] = Field(default_factory=dict)
    current_cognitive_state: Dict[str, float] = Field(default_factory=dict)
    introspection_depth: float = Field(default=0.0, ge=0, le=1)
    error: Optional[str] = None

class ErrorResilience:
    """Classe principal para funcionalidades de resiliência a erros"""
    
    @staticmethod
    def validate_reflection_request(focus_area: str) -> Dict[str, Any]:
        """Valida uma requisição de auto-reflexão"""
        try:
            validated = SelfReflectionRequest(focus_area=focus_area)
            return {"valid": True, "focus_area": validated.focus_area}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def validate_awareness_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma resposta de auto-consciência"""
        try:
            validated = SelfAwarenessResponse(**response)
            return {"valid": True, "response": validated.dict()}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def validate_json_payload(raw_data: str) -> dict:
        """
        Safely validate and parse JSON payload with comprehensive error handling
        
        Args:
            raw_data: Raw JSON string to parse
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If JSON is invalid
        """
        try:
            if not raw_data.strip():
                raise ValueError("Empty payload")
                
            return json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            raise ValueError(f"Invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected payload error: {str(e)}")
            raise ValueError(f"Bad request: {str(e)}")
    
    @staticmethod
    def safe_dict_access(data: dict, key: str, default: Any = None) -> Any:
        """
        Safely access dictionary keys with fallback
        
        Args:
            data: Dictionary to access
            key: Key to access
            default: Default value if key doesn't exist
            
        Returns:
            Value or default
        """
        try:
            if isinstance(data, dict):
                return data.get(key, default)
            else:
                logger.warning(f"Expected dict, got {type(data)} for key {key}")
                return default
        except Exception as e:
            logger.error(f"Error accessing key {key}: {str(e)}")
            return default
    
    @staticmethod
    def safe_float_conversion(value: Any, default: float = 0.0) -> float:
        """
        Safely convert value to float
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Float value or default
        """
        try:
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert {value} to float, using default {default}")
            return default
    
    @staticmethod
    def safe_list_access(data: Any, index: int, default: Any = None) -> Any:
        """
        Safely access list elements
        
        Args:
            data: List to access
            index: Index to access
            default: Default value if index doesn't exist
            
        Returns:
            Element or default
        """
        try:
            if isinstance(data, list) and 0 <= index < len(data):
                return data[index]
            else:
                return default
        except Exception as e:
            logger.error(f"Error accessing list index {index}: {str(e)}")
            return default

class MCPErrorHandler:
    """Specialized error handler for MCP server functions"""
    
    @staticmethod
    def handle_self_reflection_error(func: Callable) -> Callable:
        """
        Decorator to handle errors in self-reflection functions
        """
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # Validate result structure
                if not isinstance(result, dict):
                    logger.error(f"Expected dict result from {func.__name__}, got {type(result)}")
                    return {
                        "error": "Invalid result format",
                        "message": "Function returned unexpected data type"
                    }
                
                # Ensure required fields exist
                required_fields = ["meta_awareness", "new_insights", "self_narrative", "current_cognitive_state"]
                for field in required_fields:
                    if field not in result:
                        result[field] = {} if field in ["self_narrative", "current_cognitive_state"] else []
                
                return result
                
            except AttributeError as e:
                logger.error(f"AttributeError in {func.__name__}: {str(e)}")
                return {
                    "error": "Missing attribute",
                    "message": f"Required attribute not found: {str(e)}"
                }
            except TypeError as e:
                logger.error(f"TypeError in {func.__name__}: {str(e)}")
                return {
                    "error": "Type error",
                    "message": f"Invalid data type: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                return {
                    "error": "Internal error",
                    "message": f"Unexpected error occurred: {str(e)}"
                }
        
        return wrapper
    
    @staticmethod
    def validate_hephaestus_response(response: Any) -> Dict[str, Any]:
        """
        Validate and sanitize Hephaestus agent responses
        
        Args:
            response: Raw response from Hephaestus agent
            
        Returns:
            Validated and sanitized response
        """
        try:
            # Handle None responses
            if response is None:
                return {
                    "error": "No response",
                    "message": "Agent returned no response"
                }
            
            # Handle string responses
            if isinstance(response, str):
                try:
                    # Try to parse as JSON
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Return as plain text response
                    return {
                        "message": response,
                        "raw_response": True
                    }
            
            # Handle dict responses
            if isinstance(response, dict):
                # Ensure all values are JSON serializable
                sanitized = {}
                for key, value in response.items():
                    try:
                        json.dumps(value)  # Test serialization
                        sanitized[key] = value
                    except (TypeError, ValueError):
                        sanitized[key] = str(value)
                return sanitized
            
            # Handle other types
            return {
                "message": str(response),
                "raw_response": True
            }
            
        except Exception as e:
            logger.error(f"Error validating Hephaestus response: {str(e)}")
            return {
                "error": "Response validation failed",
                "message": f"Could not validate response: {str(e)}"
            }

class RecoveryMechanism:
    """Mechanisms for recovering from failures"""
    
    @staticmethod
    def create_fallback_response(original_error: str, context: str = "") -> Dict[str, Any]:
        """
        Create a fallback response when primary functionality fails
        
        Args:
            original_error: Original error message
            context: Context of the failure
            
        Returns:
            Fallback response
        """
        return {
            "error": "Service temporarily unavailable",
            "message": f"Primary service failed: {original_error}",
            "fallback": True,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3, backoff_factor: float = 2.0):
        """
        Retry function with exponential backoff
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            backoff_factor: Backoff multiplier
            
        Returns:
            Function result or None if all retries failed
        """
        import time
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"All retries failed for {func.__name__}: {str(e)}")
                    return None
                
                wait_time = backoff_factor ** attempt
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
        
        return None