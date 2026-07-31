"""
Presentation Layer: Pydantic Data Validation & Serialization Schemas
ทำหน้าที่รับข้อมูลจาก HTTP Request และตรวจสอบความถูกต้อง (Validation)
พร้อมทั้งแปลงรูปแบบผลลัพธ์ (Serialization) ส่งย้อนกลับไปหา Client
ตามหลักการ SoC:Presentation Layer สนใจเฉพาะสัญญาข้อมูล (API Contract) และ Data Validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    """Schema สำหรับการลงทะเบียนสมัครสมาชิก (Register / Signin)"""
    username: str = Field(..., min_length=3, max_length=50, description="ชื่อผู้ใช้งาน (Username)")
    email: EmailStr = Field(..., description="อีเมลสำหรับติดต่อและเข้าสู่ระบบ")
    password: str = Field(..., min_length=6, description="รหัสผ่านอย่างน้อย 6 ตัวอักษร")
    full_name: Optional[str] = Field(None, max_length=100, description="ชื่อ-นามสกุลจริงของผู้ใช้")


class UserLoginRequest(BaseModel):
    """Schema สำหรับการเข้าสู่ระบบ (Login)"""
    username_or_email: str = Field(..., description="Username หรือ Email ของผู้ใช้")
    password: str = Field(..., description="รหัสผ่าน")


class TokenResponse(BaseModel):
    """Schema ตอบกลับ JWT Token เมื่อ Login สำเร็จ"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema สำหรับการขอ Refresh Access Token ใหม่"""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema ตอบกลับข้อมูลรายละเอียดผู้ใช้ (Response DTO)"""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
