import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name: str) -> logging.Logger:
    # 1. เรียกใช้งาน Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # รับข้อมูลทุกระดับเพื่อส่งต่อให้ Handlers กรองต่อ

    # ป้องกันการบันทึก Log ซ้ำซ้อนเมื่อถูกเรียกใช้งานหลายครั้ง
    if logger.hasHandlers():
        return logger

    # 2. กำหนด Format ของข้อความ Log
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 3. สร้าง Console Handler (พ่นออก Terminal ระดับ INFO ขึ้นไป)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 4. สร้าง File Handler (บันทึกระดับ DEBUG ขึ้นไป พร้อมทำ Log Rotation)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,  # จำกัดขนาดไฟล์ละ 5MB
        backupCount=5,             # เก็บไฟล์ย้อนหลังสูงสุด 5 ไฟล์ (app.log.1, app.log.2, ...)
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
