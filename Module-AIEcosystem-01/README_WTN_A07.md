# Assignment WTN-A07: Trainer Worker (Token Classification Queue)

## สิ่งที่ทำไป (What Was Done)
* **พัฒนา Delayed Task Queue**: สร้าง API ด้วย FastAPI สั่งเพิ่มคิวการเทรนโมเดลลง Redis (ผ่าน ARQ) แบบกำหนดเวลาหน่วง (ETA) ให้ Worker เริ่มทำงาน ณ เวลาที่กำหนดจริง
* **เชื่อมต่อ MinIO Storage**: นำเข้า Dataset (wnut_17) จาก Hugging Face Hub แปลงเป็นฟอร์แมต JSONL อัปโหลดเข้า Bucket `datasets` และเมื่อเทรนเสร็จสิ้นจะอัปโหลดไฟล์โมเดลพร้อม `training.log` ไปยัง Bucket `models`
* **พัฒนา Trainer Worker (GPU)**: Fine-tune โมเดล Token Classification (NER) อ้างอิงตาม Hugging Face LLM Course Chapter 7 ประมวลผลบน NVIDIA GPU และบันทึกประวัติการเทรนลงไฟล์ `training.log`

## ไฟล์ที่เพิ่มเข้ามาใหม่ (Added Files)
* `backend/api/v1/training_router.py`: API Endpoints (`/init-dataset` และ `/enqueue`)
* `backend/schemas/training.py`: Pydantic Validation Schemas สำหรับรับส่งข้อมูล
* `backend/services/minio_service.py`: Business logic การจัดการ MinIO Storage และอัปโหลด Dataset
* `backend/services/training_service.py`: Business logic การส่งคิว Delayed Task ไปยัง Redis
* `backend/worker/trainer.py`: โค้ด Fine-tune PyTorch/Transformers Token Classification, บันทึก Log และอัปโหลดโมเดลขึ้น MinIO
* `backend/worker/worker.py`: ARQ Worker Process entrypoint คอยเฝ้าคิวงานใน Redis
* `backend/Dockerfile`: Dockerfile สำหรับ FastAPI Web Server
* `backend/Dockerfile.worker`: Dockerfile (PyTorch CUDA) สำหรับ GPU Trainer Worker
* `compose.yml`: เพิ่ม Service `backend` และ `trainer_worker` พร้อมเปิดใช้งาน NVIDIA GPU (`capabilities: [gpu]`)
* `.dockerignore` & `backend/.dockerignore`: ข้ามการคัดลอกไฟล์ขยะและ `.venv` เพื่อสปีดการ Build
