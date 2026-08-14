# Data Access Layer (`/repositories`)

Directory นี้ทำหน้าที่เป็น **Data Access Layer (Repository Pattern)** ของระบบ ตามหลักการ **Layered Architecture**

## โครงสร้างภายใน (`/repositories`)

- `user_repository.py`: คลาสจัดการ CRUD Operations ทั้งหมดที่เกี่ยวกับ User Entity กับฐานข้อมูลผ่าน SQLAlchemy ORM

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **Database Queries Abstraction**: ซ่อนคำสั่ง SQL / SQLAlchemy Query ไว้ภายใน Repository
2. **Encapsulation**: ทำหน้าที่เป็น Layer ขั้นกลางระหว่าง Business Logic (`services/`) กับ Database (`models/`)
3. **Reusability & Maintainability**: หากมีการเปลี่ยนโครงสร้าง Database Query หรือ ย้ายไปใช้ Database อื่น แก้ไขเพียงแค่ใน Repository ไม่กระทบ Service หรือ Router
