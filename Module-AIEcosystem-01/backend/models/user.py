"""
Data Layer: User SQLAlchemy ORM Model
ทำหน้าที่กำหนดโครงสร้างตาราง 'users' ในฐานข้อมูล
ตามหลักการ SoC: Data Layer มีหน้าที่กำหนด Entity และจัดเก็บข้อมูลลงใน DB เท่านั้น
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="user", nullable=False)  # e.g., 'user', 'admin', 'developer'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
