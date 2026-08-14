# Presentation Layer (`/api`)

Directory นี้ทำหน้าที่เป็น **Presentation Layer / API Routing** ของระบบ ตามหลักการ **Layered Architecture** และ **Separation of Concerns (SoC)**

## โครงสร้างภายใน (`/api`)

- `v1/`: ไดเรกทอรีเก็บ REST API Router แยกตามเวอร์ชันของระบบ (API Versioning)
  - `auth_router.py`: REST API Endpoints สำหรับระบบ Authentication (Login, Register, Refresh Token, Profile)
- `dependencies.py`: Dependency Injection Functions สำหรับ FastAPI (เช่น การจัดสรร Database Session, Auth Services, Current User Extraction)

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **HTTP Endpoints Definition**: รับ Request ทาง HTTP (GET, POST, PUT, DELETE) และกำหนด Path/URL
2. **Request Data Binding & Validation**: ทำงานร่วมกับ `schemas/` (Pydantic) เพื่อตรวจสอบความถูกต้องของพารามิเตอร์และ Request Body
3. **Delegation**: ส่งต่อข้อมูลให้ Business Logic Layer (`services/`) ประมวลผล โดยไม่เขียน Business Logic หรือ Query Database ซ้ำใน Router
4. **Response Mapping & Documentation**: แปลงข้อมูลผลลัพธ์กลับเป็น HTTP Response พร้อมใส่ Metadata สำหรับ Swagger/OpenAPI Documentation (`summary`, `description`, `status_code`, `response_model`)
