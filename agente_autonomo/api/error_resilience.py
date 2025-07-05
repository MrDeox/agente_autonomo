"""
Error resilience module for Hephaestus MCP Server

Provides defensive programming patterns and Pydantic validation
for critical self-awareness endpoints.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import logging

logger = logging.getLogger("HephaestusErrorResilience")

class SelfReflectionRequest(BaseModel):
    """Pydantic model for self-reflection requests"""
    focus_area: str = Field(
        default="general",
        description="Area of focus for reflection",
        min_length=1,
        max_length=100,
        regex=r"^[a-zA-Z0-9_\\-\\s]+$"
    )
    depth: Optional[int] = Field(
        default=1,
        ge=1,
        le=10,
        description="Depth of reflection (1-10)"
    )

    @validator('focus_area')
    def validate_focus_area(cls, v):
        """Additional validation for focus area"""
        if v.strip() == "":
            raise ValueError("Focus area cannot be empty")
        return v

class SelfAwarenessResponse(BaseModel):
    """Standardized response format for self-awareness endpoints"""
    meta_awareness_score: float = Field(..., ge=0, le=1)
    current_cognitive_state: dict
    insights: list[str]
    warnings: list[str] = []
    errors: list[str] = []

class ErrorResilience:
    """Core error resilience functionality"""
    
    @staticmethod
    def validate_json_payload(raw_data: str) -> dict:
        """
        Safely validate and parse JSON payload with comprehensive error handling
        
        Args:
            raw_data: Raw JSON string to parse
            
        Returns:
            Parsed JSON data
            
        Raises:
            HTTPException: If JSON is invalid
        """
        try:
            if not raw_data.strip():
                raise ValueError("Empty payload")
                
            return json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail={"error": "Invalid JSON", "message": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected payload error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={"error": "Bad request", "message": str(e)}
            )
    
    @staticmethod
    def handle_server_errors(func):
        """
        Decorator to standardize error handling for server endpoints
        """
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Server error in {func.__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Internal server error", "message": str(e)}
                )
        return wrapper
    
    @staticmethod
    def validate_response_data(data: dict) -> SelfAwarenessResponse:
        """
        Validate and standardize response data
        """
        try:
            return SelfAwarenessResponse(**data)
        except Exception as e:
            logger.error(f"Response validation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Response validation failed", "message": str(e)}
            )