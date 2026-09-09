"""
Inference Worker Core Logic
คอยดึงงานทำนายผล (Inference Job) จาก Redis Queue และประมวลผลผ่าน MLflow Model Pipeline
"""

import json
import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from schemas.inference import PredictRequest
from services.mlflow_service import mlflow_service

async def run_inference_job(ctx, job_payload: dict):
    """
    Task handler สำหรับประมวลผลการทำนายแบบ Asynchronous ผ่าน Redis Queue
    """
    job_id = job_payload.get("job_id", "unknown")
    text = job_payload.get("text", "")
    run_id = job_payload.get("run_id")

    print(f"\n[Inference Worker] >>> 🧠 กำลังประมวลผล Inference Job: {job_id} <<<", flush=True)
    print(f"[Inference Worker] Input Text: '{text}' (Run ID: {run_id})\n", flush=True)

    # บันทึกสถานะกำลังทำงานลง Redis
    redis = ctx['redis']
    await redis.set(f"job_status:{job_id}", "processing")

    # รันการทำนายใน thread pool
    loop = asyncio.get_event_loop()
    req = PredictRequest(text=text, run_id=run_id)
    pred_res = await loop.run_in_executor(None, mlflow_service.predict_entities, req)

    # แปลงผลลัพธ์เป็น dict / json และบันทึกลง Redis (หมดอายุใน 1 วัน)
    result_dict = pred_res.model_dump()
    await redis.set(f"job_result:{job_id}", json.dumps(result_dict), ex=86400)
    await redis.set(f"job_status:{job_id}", "completed")

    print(f"[Inference Worker] >>> ✅ ทำนายผลสำเร็จ Job {job_id}! พบ Entities: {len(pred_res.entities)} รายการ <<<\n", flush=True)
    return result_dict
