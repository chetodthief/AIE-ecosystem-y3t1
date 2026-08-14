# Business Logic Layer (`/services`)

Directory นี้ทำหน้าที่เป็น **Business Logic Layer (Domain Services)** ของระบบ ตามหลักการ **Layered Architecture**

## โครงสร้างภายใน (`/services`)

- `auth_service.py`: บริการจัดการตรรกะทางธุรกิจด้าน Authentication ทั้งหมด เช่น การตรวจสอบผู้ใช้ซ้ำ, การเปรียบเทียบรหัสผ่านด้วย Hashing, การสร้าง JWT Tokens และการตรวจสอบ Refresh Token

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **Core Business Logic**: บรรจุ กฎ และ ตรรกะการทำงานหลักของระบบ (Business Rules)
2. **Orchestration**: ประสานงานระหว่าง Data Access Layer (`repositories/`) กับ Infrastructure Layer (`core/`)
3. **Decoupling**: แยกตรรกะทางธุรกิจออกจาก HTTP Layer (`api/`) และ Database Access (`repositories/`) ทำให้สามารถทำ Unit Test ได้ง่ายโดยไม่ต้องเปิด Web Server
