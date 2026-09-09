"""
Business Logic Layer: MinIO Object Storage Service
จัดการสร้าง Bucket, อัปโหลด Dataset จาก Hugging Face, และจัดการไฟล์ใน MinIO
"""

import os
import json
import io
from minio import Minio
from core.config import settings

class MinIOService:
    def __init__(self):
        # สร้าง MinIO Client connection
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        for b in ["datasets", "models", "mlflow-artifacts"]:
            self.ensure_bucket_exists(b)

    def ensure_bucket_exists(self, bucket_name: str):
        """ตรวจสอบและสร้าง Bucket หากยังไม่มี"""
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def import_huggingface_dataset(self, dataset_name: str = "wnut_17", target_bucket: str = "datasets"):
        """
        โหลด Dataset จาก Hugging Face และบันทึกเป็น JSONL เก็บเข้า MinIO Bucket
        """
        from datasets import load_dataset

        self.ensure_bucket_exists(target_bucket)
        
        # โหลด Dataset จาก Hugging Face (ใช้ modern parquet datasets บน HF Hub)
        print(f"[MinIOService] โหลด Dataset '{dataset_name}' จาก Hugging Face...")
        ds = None
        candidates = [dataset_name, f"erikt/{dataset_name}", "erikt/conll2003", "lhoestq/conll2003"]
        last_err = None
        
        for name in candidates:
            try:
                ds = load_dataset(name, trust_remote_code=True)
                print(f"[MinIOService] โหลดสำเร็จจาก '{name}'!")
                dataset_name = dataset_name if dataset_name else "conll2003"
                break
            except Exception as e:
                last_err = e
                continue
                
        if ds is None:
            raise Exception(f"Failed to load dataset from HF Hub candidates: {last_err}")

        num_rows = {}
        # แปลงเป็น JSONL และอัปโหลดไปยัง MinIO
        for split in ds.keys():
            split_data = ds[split]
            num_rows[split] = len(split_data)
            
            # Serialize เป็น JSONL bytes
            buffer = io.BytesIO()
            for record in split_data:
                line = json.dumps(record, ensure_ascii=False) + "\n"
                buffer.write(line.encode('utf-8'))
            
            buffer.seek(0)
            object_name = f"{dataset_name}/{split}.jsonl"
            
            # อัปโหลดไปยัง MinIO
            self.client.put_object(
                bucket_name=target_bucket,
                object_name=object_name,
                data=buffer,
                length=buffer.getbuffer().nbytes,
                content_type="application/jsonlines"
            )
            print(f"[MinIOService] อัปโหลดสำเร็จ: {target_bucket}/{object_name} ({len(split_data)} รายการ)")

        return {
            "dataset_name": dataset_name,
            "target_bucket": target_bucket,
            "minio_path": f"{target_bucket}/{dataset_name}/",
            "num_rows": num_rows
        }

minio_service = MinIOService()
