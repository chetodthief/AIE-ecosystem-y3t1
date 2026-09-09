"""
Trainer Worker Process Entrypoint (ARQ Delayed Task Queue)
คอยดึงงานจาก Redis (คิว run_training_job) และสั่งประมวลผลการเทรนเมื่อถึงเวลาที่กำหนด
"""

import asyncio
import os
import sys
from arq.connections import RedisSettings
from worker.trainer import train_token_classification_model
from worker.inference_worker import run_inference_job

# อ่านการตั้งค่าจาก Environment Variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

async def run_training_job(ctx, job_payload: dict):
    """
    Task handler สำหรับเทรนโมเดล AI เมื่อถึงเวลาที่กำหนด (Delayed Execution)
    """
    job_id = job_payload.get("job_id", "unknown")
    print(f"\n[Trainer Worker] >>> 🚀 ถึงเวลารัน Task: {job_id} <<<")
    print(f"[Trainer Worker] Payload: {job_payload}\n")
    
    # รันการเทรนผ่าน Sync Trainer ใน thread pool (เนื่องจาก PyTorch Trainer เป็น Synchronous)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        train_token_classification_model,
        job_payload,
        MINIO_ENDPOINT,
        MINIO_ACCESS_KEY,
        MINIO_SECRET_KEY,
        False
    )
    
    print(f"\n[Trainer Worker] >>> ✅ เทรนเสร็จสิ้น Job {job_id}! ผลลัพธ์ถูกเก็บใน MinIO: {result['minio_model_path']} <<<\n")
    return result

class WorkerSettings:
    functions = [run_training_job, run_inference_job]
    redis_settings = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)
    max_jobs = 4
    job_timeout = 3600  # 1 hour timeout for background jobs
