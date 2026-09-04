"""
Presentation Layer: Pydantic Validation Schemas for Training Queue & MinIO Dataset Integration
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DatasetImportRequest(BaseModel):
    dataset_name: str = Field(default="wnut_17", description="Hugging Face Dataset name (e.g. wnut_17, conll2003)")
    target_bucket: str = Field(default="datasets", description="MinIO target bucket name")

class DatasetImportResponse(BaseModel):
    message: str
    dataset_name: str
    minio_path: str
    num_rows: Optional[Dict[str, int]] = None

class TrainEnqueueRequest(BaseModel):
    model_name: str = Field(default="bert-base-uncased", description="Pretrained model identifier")
    dataset_name: str = Field(default="wnut_17", description="Dataset stored in MinIO")
    delay_seconds: int = Field(default=10, description="Delay in seconds before worker starts execution (ETA)")
    epochs: int = Field(default=3, description="Number of training epochs")
    batch_size: int = Field(default=16, description="Training batch size per device")
    learning_rate: float = Field(default=5e-5, description="Learning rate")

class TrainJobResponse(BaseModel):
    job_id: str
    status: str
    scheduled_at: datetime
    message: str
    model_name: str
    dataset_name: str
