"""
Presentation Layer: Authentication Router (APIRouter)
ทำหน้าที่กำหนด HTTP Endpoints สำหรับ Authentication API (Domain-Based Design)
ประกอบด้วย:
- POST /api/v1/auth/register : สมัครสมาชิก
- POST /api/v1/auth/login    : เข้าสู่ระบบ
- POST /api/v1/auth/refresh  : ขอ Access Token ใหม่
- GET  /api/v1/auth/me       : ดูข้อมูลผู้ใช้งานปัจจุบัน

ตามหลักการ SoC: Router มีหน้าที่เพียงรับคำขอ (Request) เรียก Service และส่งคำตอบกลับ (Response)
พร้อมกำหนด HTTP Status Code และจับ Exception แปลงเป็น HTTP Response ที่เหมาะสม
"""

from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from services.auth_service import AuthService
from api.dependencies import get_auth_service, get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="สมัครสมาชิกใหม่ (Sign Up / Register)",
    description="รับข้อมูลสมัครสมาชิก ตรวจสอบความถูกต้อง เข้ารหัสรหัสผ่าน และสร้างบัญชีผู้ใช้ใหม่ในระบบ"
)
def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = auth_service.register_user(request)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="เข้าสู่ระบบ (Login / Sign In)",
    description="ตรวจสอบข้อมูลประจำตัว (Username/Email & Password) และคืนค่า JWT Access Token กับ Refresh Token"
)
def login(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        tokens = auth_service.authenticate_user(request)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="ขอ Access Token ใหม่ด้วย Refresh Token",
    description="รับ Refresh Token เพื่อออก Access Token ฉบับใหม่โดยไม่ต้องให้ผู้ใช้กรอก Password ซ้ำ"
)
def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        tokens = auth_service.refresh_access_token(request.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="ดูข้อมูลโปรไฟล์ของผู้ใช้งานปัจจุบัน (Current User Profile)",
    description="ต้องแนบ Header Authorization: Bearer <access_token> เพื่อเรียกดูข้อมูล"
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
