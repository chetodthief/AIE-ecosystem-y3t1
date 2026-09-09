"""
Presentation Layer: Pydantic Validation Schemas for Model Inference & Prediction APIs
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any

class PredictRequest(BaseModel):
    text: str = Field(
        default="Elon Musk is the CEO of Tesla and SpaceX in California.",
        description="Text snippet for Named Entity Recognition (Token Classification)"
    )
    model_name: Optional[str] = Field(
        default="Token-Classification-Model",
        description="Registered model name in MLflow Model Registry"
    )
    run_id: Optional[str] = Field(
        default=None,
        description="Specific MLflow Run ID to load model from (optional)"
    )

class EntityResult(BaseModel):
    word: str
    entity_group: str
    score: float

class PredictResponse(BaseModel):
    text: str
    entities: List[EntityResult]
    model_uri: str
    execution_time_sec: float
    message: str

class AsyncPredictRequest(BaseModel):
    text: str = Field(
        default="Apple Inc. announced new products in Cupertino.",
        description="Input text for asynchronous prediction job"
    )
    run_id: Optional[str] = Field(default=None, description="Specific MLflow Run ID (optional)")

class AsyncPredictJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
