# Domain Data Models Layer (`/models`)

Directory นี้ทำหน้าที่เก็บ **SQLAlchemy ORM Data Models** ซึ่งเป็นตัวแทนโครงสร้างตารางในฐานข้อมูล (Database Schema)

## โครงสร้างภายใน (`/models`)

- `user.py`: ORM Model สำหรับตาราง `users` (เก็บบัญชีผู้ใช้, รหัสผ่านที่ Hash แล้ว, บทบาท/Role, และ Timestamps)

## หน้าที่และความรับผิดชอบ (Responsibilities)
1. **ORM Mapping**: กำหนด Relationship, Table Name, Columns, Data Types, Primary Keys, Unique Constraints และ Indexes
2. **Persistence Specification**: ทำงานร่วมกับ SQLAlchemy `Base` ในการสร้าง/จัดการ Migration หรือ auto-create tables
