"""
Data Layer: Database Connection & Session Management
ทำหน้าที่สร้าง Database Engine, SessionFactory และ Base Class สำหรับ ORM Models
ตามหลักการ SoC: แยกโค้ดการเชื่อมต่อฐานข้อมูลออกจาก Router และ Business Logic
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# ตรวจสอบว่าหากเป็น SQLite ต้องใส่ check_same_thread=False
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# 1. Create SQLAlchemy Engine
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug_mode
)

# 2. Session Factory สำหรับเปิด/ปิด Transaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class สำหรับ ORM Models
Base = declarative_base()


def get_db():
    """
    Application Layer Dependency: Database Session Generator
    ใช้สำหรับ Dependency Injection (`Depends(get_db)`) ใน FastAPI
    เพื่อจัดการ Life Cycle การเปิด/ปิด Connection โดยอัตโนมัติ
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
