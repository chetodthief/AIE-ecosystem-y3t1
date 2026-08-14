# Infrastructure & Core Configuration (`/core`)

Directory นี้ทำหน้าที่จัดการ **Core Infrastructure, Configuration & Utility Modules** ของระบบ

## โครงสร้างภายใน (`/core`)

- `config.py`: โหลดตั้งค่าสภาพแวดล้อมระบบ (Environment Variables / `.env`) ผ่าน `pydantic-settings`
- `database.py`: ตั้งค่า SQLAlchemy Engine, SessionLocal, และ Base Class สำหรับติดต่อ SQLite / PostgreSQL
- `security.py`: รวม Utility Functions ด้านความปลอดภัย เช่น Hashing Passwordด้วย bcrypt, การออก/ตรวจ JWT Access Token & Refresh Token
- `logger.py`: การตั้งค่าระบบ Logging เพื่อบันทึกพฤติกรรมหรือข้อผิดพลาดของระบบลงไฟล์และ Console

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **Centralized Configuration**: รวมจุดตั้งค่าสำคัญของแอพไว้ที่เดียว
2. **Infrastructure Services**: เตรียมการเชื่อมต่อ Database, Cryptography, และ System Logging
