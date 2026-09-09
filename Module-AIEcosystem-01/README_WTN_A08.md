# Assignment WTN-A08: MLflow Tracking Server & Inference Worker

## สิ่งที่ทำไป 
* **เพิ่มระบบ MLflow MLOps Platform**: ติดตั้ง MLflow Tracking Server เชื่อมต่อกับ PostgreSQL (`school_db`) สำหรับเก็บ Metadata/Metrics และเชื่อมต่อ MinIO (`s3://mlflow-artifacts/`) สำหรับเก็บ Model Artifacts
* **ปรับปรุง Trainer Worker ร่วมกับ MLflow**: บันทึก Parameters (`epochs`, `batch_size`, `learning_rate`), Metrics (`train_loss`), และลงทะเบียนตัวโมเดลเข้า MLflow Model Registry (`Token-Classification-Model`) ทันทีเมื่อเทรนเสร็จ
* **สร้าง Inference Worker & Prediction APIs**: พัฒนาระบบทำนายผลคำศัพท์ (NER Entity Tagging) โดยโหลดโมเดลจาก MLflow มาประมวลผล ให้บริการทั้งแบบ Synchronous (`POST /predict`), Asynchronous Queue (`POST /enqueue-predict`) และขอดูผลงานผ่าน `job_id` (`GET /jobs/{job_id}`)

## ไฟล์ที่เพิ่มเข้ามาใหม่และแก้ไข (Added & Modified Files)
* `backend/Dockerfile.mlflow`: Dockerfile สำหรับสร้างคอนเทนเนอร์ MLflow Server
* `backend/api/v1/inference_router.py`: API Endpoints สำหรับ `/predict`, `/enqueue-predict`, และ `/jobs/{job_id}`
* `backend/schemas/inference.py`: Pydantic Schemas สำหรับ Prediction Request & Response
* `backend/services/mlflow_service.py`: Business logic โหลดโมเดลจาก MLflow Model Registry และทำนายผล
* `backend/services/inference_service.py`: Business logic การจัดการ Async Prediction Queue ผ่าน Redis
* `backend/worker/trainer.py`: ปรับแก้ไขให้ส่ง Parameters, Metrics และ Model Artifacts เข้า MLflow
* `backend/worker/inference_worker.py`: Worker Process สำหรับประมวลผลคำขอทำนายแบบ Async
* `backend/worker/worker.py`: ปรับแก้ไขให้รองรับทั้ง `run_training_job` และ `run_inference_job`
* `backend/main.py`: ลงทะเบียน `inference_router` เข้ากับ FastAPI
* `compose.yml`: เพิ่ม Service `mlflow` และ `inference_worker` พร้อมตั้งค่า Environment Variables
* `REPORT_WTN_A08_DOCS.md`: รายงานสรุปฉบับเต็มภาษาไทยสำหรับ Google Docs / เขียนมือ PDF (ตอบโจทย์ข้อ 1-2)
