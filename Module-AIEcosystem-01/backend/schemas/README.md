# Data Transfer Objects / Schemas Layer (`/schemas`)

Directory นี้ทำหน้าที่เก็บ **Pydantic Schemas (DTOs - Data Transfer Objects)** สำหรับตรวจสอบ ความถูกต้องของข้อมูล (Validation) ทั้งฝั่ง Request และ Response

## โครงสร้างภายใน (`/schemas`)

- `auth.py`: Pydantic Models สำหรับ Authentication เช่น `UserRegisterRequest`, `UserLoginRequest`, `TokenResponse`, `RefreshTokenRequest`, `UserResponse`

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **Request Data Validation**: ตรวจสอบ ชนิดข้อมูล, ความยาวรหัสผ่าน, รูปแบบ Email ก่อนเข้าสู่ Service Layer
2. **Response Serialization**: กำหนดโครงสร้าง JSON Output ที่ส่งกลับให้ Client (เช่น ไม่ส่ง `hashed_password` ออกไป)
3. **OpenAPI Doc Generation**: ช่วยสร้าง Field Descriptions และ Examples ใน Swagger UI / OpenAPI Spec
