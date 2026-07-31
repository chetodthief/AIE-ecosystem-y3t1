"""
Application Layer: FastAPI Dependency Injection Registry
ศูนย์รวมการฉีด Dependency (`Depends()`) ของระบบ
ตามหลักการ SoC & Reusability:
- ช่วยให้ทุก Endpoint ใช้มาตรฐานเดียวกันในการดึง Session, Service และตรวจ Authorization
- ลดการเขียนโค้ดซ้ำ (DRY Principle)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from core.security import decode_token
from models.user import User

# Schema OAuth2 สำหรับอ่าน Bearer Token จาก Header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency สำหรับฉีด UserRepository"""
    return UserRepository(db)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    """Dependency สำหรับฉีด AuthService"""
    return AuthService(user_repo)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency สำหรับยืนยันตัวตนผู้ใช้ใน Endpoint ที่ต้องการ Authorization Header
    1. อ่านและ Decode Token
    2. ค้นหาผู้ใช้จาก Database
    3. ส่งคืนค่านวัตกรรม User Object ปัจจุบัน
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
            
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user
