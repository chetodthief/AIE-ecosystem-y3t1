"""
Presentation Layer: Inference & Prediction API Router
ให้บริการ Endpoints สำหรับสั่งทำนายผลโมเดล (Predict) ทั้งแบบ Synchronous และ Asynchronous
"""

from fastapi import APIRouter, HTTPException, status
from schemas.inference import (
    PredictRequest,
    PredictResponse,
    AsyncPredictRequest,
    AsyncPredictJobResponse
)
from services.mlflow_service import mlflow_service
from services.inference_service import inference_service

router = APIRouter(prefix="/inference", tags=["Model Inference & Prediction"])

@router.post("/predict", response_model=PredictResponse, summary="สั่งทำนายคำศัพท์ (NER) แบบ Synchronous ผ่าน MLflow Model")
def predict_sync(req: PredictRequest):
    """
    รับข้อความ (Text) และดึงโมเดล Token Classification ล่าสุดจาก MLflow มาวิเคราะห์หาหมวดหมู่คำ (Named Entities)
    """
    try:
        return mlflow_service.predict_entities(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference prediction failed: {str(e)}"
        )

@router.post("/enqueue-predict", response_model=AsyncPredictJobResponse, summary="ส่งคำขอทำนายผลเข้าคิว Redis (Asynchronous)")
async def enqueue_predict_async(req: AsyncPredictRequest):
    """
    ส่งคำขอทำนายผลเข้าคิว Redis และคืนค่า job_id เพื่อนำไปขอดูผลการประมวลผลภายหลัง
    """
    try:
        return await inference_service.enqueue_inference_job(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue inference job: {str(e)}"
        )

@router.get("/jobs/{job_id}", summary="ขอดูผลการทำงานและสถานะของ Prediction Job ผ่าน job_id")
async def get_job_result(job_id: str):
    """
    ดึงสถานะและผลลัพธ์การทำนายผลจาก Redis โดยอ้างอิงผ่าน `job_id`
    """
    try:
        return await inference_service.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job status for '{job_id}': {str(e)}"
        )
