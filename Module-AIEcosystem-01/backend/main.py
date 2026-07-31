"""
FastAPI Application Entry Point
ทำหน้าที่ประกอบส่วนประกอบต่างๆ (Routers, Database Tables, Global Middleware) เข้าด้วยกัน
ตามหลักการ Layered Architecture และ Separation of Concerns (SoC)
"""

from fastapi import FastAPI
from core.config import settings
from core.database import engine, Base
from api.v1.auth_router import router as auth_router

# นำเข้า Models เพื่อให้ SQLAlchemy รู้จัก Schema ตารางในการ auto-create
import models.user  # noqa: F401

# สร้างตารางใน Database หากยังไม่มี (สำหรับ Production แนะนำให้ใช้ Alembic)
Base.metadata.create_all(bind=engine)

# สร้าง FastAPI Application Instance
app = FastAPI(
    title=settings.app_name,
    description="""
    ## AI Ecosystem Authentication API Service
    ระบบ Authentication ตัวอย่างที่ออกแบบตามแนวทาง **Separation of Concerns (SoC)**
    และ **Layered Architecture** สำหรับใช้ใน AI Ecosystem
    
    ### 4-Layer Architecture Structure:
    1. **Presentation Layer**: FastAPI APIRouter & Pydantic Validation Schemas (`schemas/`, `api/v1/`)
    2. **Application Layer**: Dependency Injection & Security Helpers (`core/security.py`, `api/dependencies.py`)
    3. **Business Logic Layer**: Domain Services (`services/auth_service.py`)
    4. **Data Layer**: Database Models & Repositories (`models/`, `repositories/`, `core/database.py`)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ลงทะเบียน Router โดยแบ่งตาม Domain และ Versioning (/api/v1/auth)
app.include_router(auth_router, prefix="/api/v1")


@app.get("/", tags=["System"])
def root():
    return {
        "app": settings.app_name,
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Monitoring API: Health Check Endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
