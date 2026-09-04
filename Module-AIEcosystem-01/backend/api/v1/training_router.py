"""
Presentation Layer: Training & MinIO Management Router
ให้ API สำหรับนำเข้า Dataset จาก Hugging Face และสั่ง Enqueue งานเทรนโมเดลแบบตั้งเวลาเริ่มได้
"""

from fastapi import APIRouter, HTTPException, status
from schemas.training import (
    DatasetImportRequest,
    DatasetImportResponse,
    TrainEnqueueRequest,
    TrainJobResponse
)
from services.minio_service import minio_service
from services.training_service import training_service

router = APIRouter(prefix="/training", tags=["Training Task Queue"])

@router.post("/init-dataset", response_model=DatasetImportResponse, summary="โหลด Dataset จาก Hugging Face ลง MinIO")
def import_dataset(req: DatasetImportRequest):
    """
    ดึงข้อมูล Dataset (เช่น wnut_17) จาก Hugging Face Hub และอัปโหลดไปยัง MinIO Bucket (datasets/)
    """
    try:
        res = minio_service.import_huggingface_dataset(
            dataset_name=req.dataset_name,
            target_bucket=req.target_bucket
        )
        return DatasetImportResponse(
            message="Imported dataset to MinIO successfully",
            dataset_name=res["dataset_name"],
            minio_path=res["minio_path"],
            num_rows=res["num_rows"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import dataset to MinIO: {str(e)}"
        )

@router.post("/enqueue", response_model=TrainJobResponse, summary="เพิ่มงานเทรนโมเดลลงคิวแบบตั้งเวลาเริ่ม (Delayed Queue)")
async def enqueue_train_job(req: TrainEnqueueRequest):
    """
    สั่งงานเทรนโมเดล Token Classification ผ่าน API ส่งเข้า Redis Queue
    สามารถตั้งค่า `delay_seconds` เพื่อให้ Trainer Worker เริ่มทำงาน ณ เวลาที่กำหนดได้
    """
    try:
        res = await training_service.enqueue_training_job(req)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue training job: {str(e)}"
        )
