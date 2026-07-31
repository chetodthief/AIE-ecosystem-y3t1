"""
Application Layer: Security & Cryptography Utilities
ทำหน้าที่เกี่ยวกับการเข้ารหัสรหัสผ่าน (Password Hashing) และการสร้าง/ตรวจสอบ JWT Tokens
ตามหลักการ Security Best Practices:
1. ไม่เก็บบันทึก Password เป็นข้อความธรรมดา (Plain Text) ลงในฐานข้อมูล
2. ใช้ bcrypt สำหรับเข้ารหัสและตรวจสอบรหัสผ่าน
3. ใช้ JWT Access Token และ Refresh Token ในการยืนยันตัวตน
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import bcrypt
import jwt
from core.config import settings


def hash_password(password: str) -> str:
    """แปลง Password ข้อความธรรมดาเป็น Password Hash โดยใช้ bcrypt"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """เปรียบเทียบ Plain Password กับ Hashed Password ในฐานข้อมูล"""
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """สร้าง JWT Access Token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """สร้าง JWT Refresh Token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """ถอดรหัสและตรวจสอบความถูกต้องของ JWT Token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid token")
