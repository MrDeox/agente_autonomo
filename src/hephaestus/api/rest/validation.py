"""
Validation module for Hephaestus MCP Server

Handles schema validation for critical API endpoints
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, validator

class SelfReflectionSchema(BaseModel):
    """Schema for deep_self_reflection endpoint"""
    meta_awareness: float
    new_insights: list
    self_narrative: Dict[str, str]
    current_cognitive_state: Dict[str, float]
    introspection_depth: float

    @validator('meta_awareness')
    def validate_meta_awareness(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('meta_awareness must be between 0 and 1')
        return v

class AwarenessReportSchema(BaseModel):
    """Schema for self_awareness_report endpoint"""
    self_awareness_metrics: Dict[str, float]
    current_cognitive_state: Dict[str, float]
    cognitive_trajectory: Dict[str, Any]
    recent_insights: list
    monitoring_status: Dict[str, Any]

    @validator('self_awareness_metrics')
    def validate_metrics(cls, v):
        required_keys = {
            'meta_awareness_score', 
            'temporal_awareness', 
            'introspection_depth',
            'cognitive_coherence',
            'self_knowledge_confidence'
        }
        if not required_keys.issubset(v.keys()):
            raise ValueError('Missing required awareness metrics')
        return v

def validate_self_reflection(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate deep_self_reflection response"""
    try:
        return SelfReflectionSchema(**data).dict()
    except Exception as e:
        raise ValueError(f"Invalid self reflection data: {str(e)}")

def validate_awareness_report(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate self_awareness_report response"""
    try:
        return AwarenessReportSchema(**data).dict()
    except Exception as e:
        raise ValueError(f"Invalid awareness report data: {str(e)}")