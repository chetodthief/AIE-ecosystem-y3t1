"""
Business Logic Layer: AuthService
รับผิดชอบกฎและกระบวนการทำงานหลัก (Business Rules) สำหรับ Authentication
เช่น:
1. การตรวจสอบว่า Username/Email ซ้ำหรือไม่ก่อนทำการ Register
2. การสั่ง Hash รหัสผ่าน และส่งต่อให้ Data Layer บันทึก
3. การตรวจสอบความถูกต้องของรหัสผ่านตอน Login และสร้าง Token
4. การต่ออายุ Access Token ด้วย Refresh Token

ตามหลักการ SoC & Loose Coupling:
- Service ไม่สนใจเรื่อง HTTP Request / Status Code (เป็นหน้าที่ของ Presentation Layer)
- Service ไม่สนใจเรื่อง SQL Statement (เป็นหน้าที่ของ Data Layer)
"""

from typing import Dict, Any
from repositories.user_repository import UserRepository
from schemas.auth import UserRegisterRequest, UserLoginRequest
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from models.user import User


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, request: UserRegisterRequest) -> User:
        """
        Business Rule: การสมัครสมาชิกใหม่
        1. ตรวจสอบว่า Username มีผู้ใช้งานอยู่แล้วหรือไม่
        2. ตรวจสอบว่า Email มีผู้ใช้งานอยู่แล้วหรือไม่
        3. เข้ารหัส Password ด้วย bcrypt
        4. เรียกใช้ UserRepository เพื่อบันทึกข้อมูล
        """
        if self.user_repo.get_by_username(request.username):
            raise ValueError("Username is already registered")

        if self.user_repo.get_by_email(request.email):
            raise ValueError("Email is already registered")

        hashed_pwd = hash_password(request.password)

        new_user = self.user_repo.create(
            username=request.username,
            email=request.email,
            hashed_password=hashed_pwd,
            full_name=request.full_name
        )
        return new_user

    def authenticate_user(self, request: UserLoginRequest) -> Dict[str, str]:
        """
        Business Rule: การยืนยันตัวตนเพื่อเข้าสู่ระบบ
        1. ค้นหาผู้ใช้ด้วย Username หรือ Email
        2. ตรวจสอบว่ามีผู้ใช้และสถานะ Active หรือไม่
        3. ตรวจสอบความถูกต้องของ Password กับ Password Hash
        4. สร้างและคืนค่า JWT Access Token และ Refresh Token
        """
        user = self.user_repo.get_by_username_or_email(request.username_or_email)
        if not user:
            raise ValueError("Invalid username/email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        if not verify_password(request.password, user.hashed_password):
            raise ValueError("Invalid username/email or password")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Business Rule: การขอ Access Token ใหม่ด้วย Refresh Token
        1. Decode Refresh Token และตรวจสอบ Expiration / Validity
        2. ตรวจสอบ Token Type ว่าเป็น 'refresh' หรือไม่
        3. ค้นหาข้อมูล User และสร้าง Access Token ใหม่
        """
        try:
            payload = decode_token(refresh_token)
        except ValueError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")

        if payload.get("type") != "refresh":
            raise ValueError("Token is not a valid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        user = self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        new_access_token = create_access_token(subject=user.id)

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
