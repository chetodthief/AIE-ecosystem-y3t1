# บรรทัดที่ 1-10 ของ minio_test.py
from minio import Minio
from minio.versioningconfig import VersioningConfig
import os
import sys

# ดึงโฟลเดอร์ parent (backend) เข้ามาใน python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# เรียกนำเข้า logger
from core.logger import get_logger
logger = get_logger("minio_sandbox")

# 1. ตั้งค่าการเชื่อมต่อ
client = Minio(
    "localhost:9000",
    access_key="minioadmin",   
    secret_key="minioadmin",   
    secure=False
)

bucket_name = "my-photos"

def setup_bucket_and_versioning():
    """สร้าง Bucket และเปิดการใช้งาน Versioning"""
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        logger.info(f" สร้าง Bucket '{bucket_name}' สำเร็จ")
    
    # เปิดใช้งาน Versioning
    client.set_bucket_versioning(bucket_name, VersioningConfig("Enabled"))
    logger.info(f" เปิดใช้งาน Versioning สำหรับ '{bucket_name}' แล้ว")

def upload_photo(file_path, object_name):
    """อัปโหลดรูปภาพเข้า MinIO"""
    try:
        result = client.fput_object(bucket_name, object_name, file_path)
        logger.info(f" อัปโหลด '{object_name}' สำเร็จ (Version ID: {result.version_id})")
        return result.version_id
    except Exception as e:
        logger.error(f" Error uploading: {e}")

def download_photo(object_name, download_path, version_id=None):
    """ดาวน์โหลดรูปภาพ โดยเลือกได้ว่าจะระบุ Version หรือไม่"""
    try:
        client.fget_object(bucket_name, object_name, download_path, version_id=version_id)
        ver_text = f" (Version: {version_id})" if version_id else " (Latest Version)"
        logger.info(f" ดาวน์โหลด '{object_name}'{ver_text} สำเร็จ -> บันทึกที่ {download_path}")
    except Exception as e:
        logger.error(f"Error downloading: {e}")

if __name__ == "__main__":
    setup_bucket_and_versioning()
    
      
    photo_v1_path = r"D:\aie y3 t1\Module-AIEcosystem-01\backend\my-photos\profile_pic.jpg" 
    photo_v2_path = r"D:\aie y3 t1\Module-AIEcosystem-01\backend\my-photos\profile_pic2.jpg" 

    print("\n--- ทดสอบ Upload และ Versioning ---")
    # 1. อัปโหลดรูปครั้งแรก (ใช้ชื่อปลายทาง profile_pic.jpg เสมอ)
    v1_id = upload_photo(photo_v1_path, "profile_pic.jpg")
    
    # 2. อัปโหลดรูปใหม่ทับชื่อเดิม (ใช้ชื่อปลายทาง profile_pic.jpg เสมอ)
    v2_id = upload_photo(photo_v2_path, "profile_pic.jpg")
    
    print("\n--- ทดสอบ Download ---")
    # 3. ดาวน์โหลดแบบ *ไม่ระบุ Version* (จะเซฟออกมาเป็น downloaded_latest.jpg)
    download_photo("profile_pic.jpg", "downloaded_latest.jpg")

    # 4. ดาวน์โหลดแบบ *ระบุ Version ของ V1* (จะเซฟออกมาเป็น downloaded_old_version.jpg)
    download_photo("profile_pic.jpg", "downloaded_old_version.jpg", version_id=v1_id)
