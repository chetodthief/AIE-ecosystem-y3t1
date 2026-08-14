# Integration Test Sandbox (`/sandbox`)

Directory นี้ทำหน้าที่เป็น **Sandbox สำหรับทดสอบการเชื่อมต่อ Library และ Component ต่างๆ ในระบบ** ก่อนนำไปยกระดับขึ้นเป็น Production Services/APIs

## โครงสร้างภายใน (`/sandbox`)

- `minio_test.py`: สคริปต์ทดสอบการเชื่อมต่อ MinIO (Object Storage) สร้าง Bucket และ Upload/Download ไฟล์
- `label_studio_test.py`: สคริปต์ทดสอบการเชื่อมต่อ Label Studio SDK (Data Labeling Platform) สร้าง Project และ Import Tasks
- `enqueue_job.py` & `worker_settings.py`: สคริปต์ทดสอบระบบ Background Task Queue (ARQ / Redis)
- `db_test.py`: สคริปต์ทดสอบการเชื่อมต่อฐานข้อมูล
- `test_auth_api.py`: สคริปต์ Integration Test สำหรับทดสอบ Flow การทำงานของ Auth APIs

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **Component Verification**: ทดสอบเชื่อมต่อ Library ของระบบภายนอก (MinIO, Label Studio, Redis/ARQ)
2. **Prototyping**: ทดลองการใช้งาน SDK/Library ก่อนเขียน Service Layer จริง
