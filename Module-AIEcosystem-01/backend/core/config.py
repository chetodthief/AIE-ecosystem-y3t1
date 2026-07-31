"""
Application Layer: Configuration Management
ดูแลจัดการค่า Config และ Environment Variables ของระบบ
ตามหลักการ SoC: ไม่ควร hardcode ค่าความลับ (Secret Keys, DB URLs) ไว้ใน Source Code
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Ecosystem API"
    debug_mode: bool = False
    
    # Database Configuration
    database_url: str = "sqlite:///./ai_ecosystem.db"
    
    # JWT Security Settings
    secret_key: str = "ai-ecosystem-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ดึงค่าจากไฟล์ .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Singleton Instance ของ Settings สำหรับดึงไปใช้งานทั่วทั้งแอปพลิเคชัน
settings = Settings()