# Backend AI Ecosystem Service

ระบบ Backend Service ที่พัฒนาด้วย **FastAPI** โดยใช้สถาปัตยกรรม **Layered Architecture (4-Layer Pattern)** และ **Separation of Concerns (SoC)**

## 📂 โครงสร้างไดเรกทอรี (Directory Structure)

```text
backend/
├── api/                  # Presentation Layer (APIRouters & Dependencies)
│   ├── v1/               # API Versioning 1 (auth_router.py)
│   └── dependencies.py   # FastAPI Dependency Injection Functions
├── core/                 # Infrastructure & System Configuration (config, database, security, logger)
├── models/               # Data Layer: SQLAlchemy ORM Models (user.py)
├── repositories/         # Data Layer: Repository Pattern (user_repository.py)
├── schemas/              # Presentation Layer: Pydantic DTOs & Validation (auth.py)
├── services/             # Business Logic Layer: Domain Services (auth_service.py)
├── sandbox/              # Sandbox สคริปต์ทดสอบการเชื่อมต่อ Libraries (MinIO, Label Studio, ARQ)
├── export_openapi_to_csv.py # สคริปต์สำหรับ Snapshot & แปลง openapi.json เป็น CSV / Excel
├── openapi.json          # ไฟล์ Snapshot OpenAPI Specification (JSON Format)
├── api_snapshot.csv      # ไฟล์ Snapshot รายการ APIs ทั้งหมดในรูปแบบ CSV / Excel
├── main.py               # จุดเริ่มต้น FastAPI Application
└── pyproject.toml        # Library and Dependency Management
```

## 🛠️ รายการ Libraries และ External Components
1. **FastAPI & Uvicorn**: Web Framework และ ASGI Server
2. **SQLAlchemy & PostgreSQL / SQLite**: Database ORM และ Data Storage
3. **MinIO (`minio`)**: Object Storage สำหรับเก็บไฟล์ภาพ/สื่อ
4. **Label Studio (`label-studio-sdk`)**: Data Annotation / Labeling Platform
5. **ARQ & Redis (`arq`)**: Asynchronous Background Task Queue
6. **Passlib & PyJWT**: Hashing Password (bcrypt) และ JWT Token Authentication

## 🚀 การใช้งานสคริปต์ Snapshot API List (ข้อ 3e)
สามารถรันสคริปต์เพื่อส่งออก `openapi.json` และ `api_snapshot.csv` ได้ดังนี้:

```bash
uv run python export_openapi_to_csv.py
```
หรือ
```bash
.venv\Scripts\python export_openapi_to_csv.py
```
*(ไฟล์ `api_snapshot.csv` ถูกเข้ารหัสแบบ UTF-8 BOM รองรับการเปิดภาษาไทยด้วย Microsoft Excel ได้ทันที)*
