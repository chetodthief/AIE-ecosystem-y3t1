"""
Data Layer: User Repository
ทำหน้าที่เป็นตัวกลางในการจัดการคำสั่ง Database (CRUD) สำหรับ User Table
ตามหลักการ SoC: แยกคำสั่งค้นหา/จัดเก็บข้อมูลออกจาก Business Logic
เมื่อมีการเปลี่ยนฐานข้อมูลหรือวิธี Query จะแก้ไขเพียงในส่วน Repository นี้เท่านั้น
"""

from typing import Optional
from sqlalchemy.orm import Session
from models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """ดึงข้อมูล User ตาม ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """ดึงข้อมูล User ตาม Username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """ดึงข้อมูล User ตาม Email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """ค้นหา User ด้วย Username หรือ Email"""
        return self.db.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

    def create(self, username: str, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        """บันทึกข้อมูล User ใหม่ลงในฐานข้อมูล"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
