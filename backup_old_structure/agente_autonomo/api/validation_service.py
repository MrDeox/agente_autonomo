"""
Validation Service for Hephaestus MCP Server

Handles schema validation and automated recovery for critical endpoints
"""
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
import logging

logger = logging.getLogger("ValidationService")

class SelfReflectionRequest(BaseModel):
    """Pydantic model for deep_self_reflection endpoint request"""
    introspection_depth: float = 0.5
    include_meta_awareness: bool = True
    include_cognitive_state: bool = True

class SelfReflectionResponse(BaseModel):
    """Pydantic model for deep_self_reflection endpoint response"""
    meta_awareness: float
    new_insights: list
    self_narrative: Dict[str, str]
    current_cognitive_state: Dict[str, float]
    introspection_depth: float

class AwarenessReportRequest(BaseModel):
    """Pydantic model for self_awareness_report endpoint request"""
    include_metrics: bool = True
    include_trajectory: bool = True
    include_insights: bool = True

class AwarenessReportResponse(BaseModel):
    """Pydantic model for self_awareness_report endpoint response"""
    self_awareness_metrics: Dict[str, float]
    current_cognitive_state: Dict[str, float]
    cognitive_trajectory: Dict[str, Any]
    recent_insights: list
    monitoring_status: Dict[str, Any]

class ValidationService:
    """Service for validating and recovering from invalid responses"""
    
    @staticmethod
    def validate_self_reflection_request(data: Dict[str, Any]) -> bool:
        """Validate deep_self_reflection request structure"""
        try:
            SelfReflectionRequest(**data)
            return True
        except ValidationError as e:
            logger.error(f"Self reflection request validation failed: {e}")
            return False
    
    @staticmethod
    def validate_self_reflection_response(data: Dict[str, Any]) -> bool:
        """Validate deep_self_reflection response structure"""
        try:
            SelfReflectionResponse(**data)
            return True
        except ValidationError as e:
            logger.error(f"Self reflection validation failed: {e}")
            return False
    
    @staticmethod
    def validate_awareness_report_request(data: Dict[str, Any]) -> bool:
        """Validate self_awareness_report request structure"""
        try:
            AwarenessReportRequest(**data)
            return True
        except ValidationError as e:
            logger.error(f"Awareness report request validation failed: {e}")
            return False
    
    @staticmethod
    def validate_awareness_report_response(data: Dict[str, Any]) -> bool:
        """Validate self_awareness_report response structure"""
        try:
            AwarenessReportResponse(**data)
            return True
        except ValidationError as e:
            logger.error(f"Awareness report validation failed: {e}")
            return False
    
    @staticmethod
    def recover_invalid_response(data: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """Attempt to recover from invalid response structure"""
        # TODO: Implement recovery logic
        return {
            "error": "Validation failed",
            "message": f"Invalid {endpoint} response structure",
            "original_data": data
        }