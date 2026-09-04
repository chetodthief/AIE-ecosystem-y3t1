"""
Business Logic Layer: Training Queue Service
จัดการ Enqueue Delayed Task สำหรับการเทรนโมเดล AI ผ่าน Redis (ARQ Queue)
"""

import uuid
from datetime import datetime, timedelta
from arq import create_pool
from arq.connections import RedisSettings
from core.config import settings
from schemas.training import TrainEnqueueRequest, TrainJobResponse

class TrainingService:
    def __init__(self):
        self.redis_settings = RedisSettings(
            host=settings.redis_host,
            port=settings.redis_port
        )

    async def enqueue_training_job(self, req: TrainEnqueueRequest) -> TrainJobResponse:
        """
        สร้าง Job ID และ enqueue งานเข้า Redis พร้อมกำหนดเวลา delay (ETA)
        """
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        scheduled_at = datetime.utcnow() + timedelta(seconds=req.delay_seconds)

        job_payload = {
            "job_id": job_id,
            "model_name": req.model_name,
            "dataset_name": req.dataset_name,
            "epochs": req.epochs,
            "batch_size": req.batch_size,
            "learning_rate": req.learning_rate,
            "scheduled_at": scheduled_at.isoformat()
        }

        # เชื่อมต่อ Redis และ enqueue job
        redis = await create_pool(self.redis_settings)
        await redis.enqueue_job(
            "run_training_job",
            job_payload,
            _job_id=job_id,
            _defer_by=req.delay_seconds  # ตั้งเวลาเริ่มทำงานตามกำหนดเวลาที่ร้องขอ
        )

        return TrainJobResponse(
            job_id=job_id,
            status="queued_delayed",
            scheduled_at=scheduled_at,
            message=f"Job {job_id} queued successfully! Will execute in {req.delay_seconds} seconds.",
            model_name=req.model_name,
            dataset_name=req.dataset_name
        )

training_service = TrainingService()
