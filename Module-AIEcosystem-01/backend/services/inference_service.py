"""
Business Logic Layer: Async Inference Queue Service
จัดการ Enqueue คิวงานทำนายผลแบบ Asynchronous ผ่าน Redis (ARQ)
"""

import uuid
from arq import create_pool
from arq.connections import RedisSettings
from core.config import settings
from schemas.inference import AsyncPredictRequest, AsyncPredictJobResponse

class InferenceService:
    def __init__(self):
        self.redis_settings = RedisSettings(
            host=settings.redis_host,
            port=settings.redis_port
        )

    async def enqueue_inference_job(self, req: AsyncPredictRequest) -> AsyncPredictJobResponse:
        """ส่งคำขอทำนายผลเข้าคิว Redis"""
        job_id = f"pred_{uuid.uuid4().hex[:8]}"
        job_payload = {
            "job_id": job_id,
            "text": req.text,
            "run_id": req.run_id
        }

        redis = await create_pool(self.redis_settings)
        await redis.enqueue_job(
            "run_inference_job",
            job_payload,
            _job_id=job_id
        )

        return AsyncPredictJobResponse(
            job_id=job_id,
            status="queued",
            message=f"Inference job {job_id} queued successfully! Query result at /api/v1/inference/jobs/{job_id}"
        )

    async def get_job_status(self, job_id: str):
        """ดึงสถานะและผลลัพธ์ของ Job จาก Redis"""
        redis = await create_pool(self.redis_settings)
        job_result = await redis.get(f"job_result:{job_id}")
        
        if not job_result:
            # Check if job is still in progress / queued
            job_status = await redis.get(f"job_status:{job_id}")
            status_str = job_status.decode() if job_status else "in_progress_or_queued"
            return {
                "job_id": job_id,
                "status": status_str,
                "result": None
            }

        import json
        result_data = json.loads(job_result.decode())
        return {
            "job_id": job_id,
            "status": "completed",
            "result": result_data
        }

inference_service = InferenceService()
