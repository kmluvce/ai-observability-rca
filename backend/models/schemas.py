from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ObservabilityData(BaseModel):
    """Schema for observability data input"""
    logs: str = Field(..., description="Log data as text")
    metrics: str = Field(..., description="Metrics data as text")
    traces: str = Field(..., description="Trace data as text")
    timestamp: Optional[datetime] = None
    system_id: Optional[str] = None
    environment: Optional[str] = "production"

class RCAResponse(BaseModel):
    """Schema for RCA analysis response"""
    analysis_id: str
    rca_result: str
    status: str
    confidence_score: Optional[float] = None
    similar_cases: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    created_at: Optional[datetime] = None

class BulkUploadResponse(BaseModel):
    """Schema for bulk upload response"""
    uploaded_files: List[Dict[str, Any]]
    total_processed: int
    status: str
    errors: Optional[List[str]] = None

class HistoricalCase(BaseModel):
    """Schema for historical case data"""
    case_id: str
    logs: str
    metrics: str
    traces: str
    rca_result: str
    timestamp: datetime
    system_id: Optional[str] = None
    environment: Optional[str] = None
    tags: Optional[List[str]] = None

class SimilarCaseResult(BaseModel):
    """Schema for similar case search results"""
    case_id: str
    similarity_score: float
    rca_summary: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
