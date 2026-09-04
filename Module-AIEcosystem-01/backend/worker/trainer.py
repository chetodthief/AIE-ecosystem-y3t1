"""
Trainer Worker Core Logic: Token Classification (Hugging Face / PyTorch)
1. ดึงข้อมูล Dataset จาก MinIO Bucket datasets/
2. ทำการ Token Alignment & Fine-tune โมเดล Token Classification (NER)
3. บันทึก Training Log ลงไฟล์ training.log
4. บันทึก Model Weights, Config, Tokenizer และ Log กลับไปที่ MinIO Bucket models/
"""

import os
import io
import json
import logging
import torch
from minio import Minio
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification
)
import numpy as np

# Configure Logging
def setup_logger(log_file_path: str):
    logger = logging.getLogger("TrainerLogger")
    logger.setLevel(logging.INFO)
    logger.handlers = [] # clear existing handlers
    
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

def download_dataset_from_minio(minio_client: Minio, dataset_name: str, local_dir: str, logger: logging.Logger):
    """ดึงไฟล์ jsonl ของ dataset จาก MinIO"""
    bucket_name = "datasets"
    os.makedirs(local_dir, exist_ok=True)
    
    objects = minio_client.list_objects(bucket_name, prefix=f"{dataset_name}/", recursive=True)
    downloaded_files = {}
    
    for obj in objects:
        filename = os.path.basename(obj.object_name)
        split = filename.replace(".jsonl", "")
        local_filepath = os.path.join(local_dir, filename)
        
        logger.info(f"Downloading {obj.object_name} from MinIO bucket '{bucket_name}' -> {local_filepath}")
        minio_client.fget_object(bucket_name, obj.object_name, local_filepath)
        downloaded_files[split] = local_filepath
        
    return downloaded_files

def load_local_jsonl_dataset(downloaded_files: dict):
    """โหลดไฟล์ JSONL เป็น Hugging Face DatasetDict"""
    ds_dict = {}
    for split, filepath in downloaded_files.items():
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        ds_dict[split] = Dataset.from_list(records)
    return DatasetDict(ds_dict)

def train_token_classification_model(
    job_payload: dict,
    minio_endpoint: str = "minio:9000",
    minio_access_key: str = "minioadmin",
    minio_secret_key: str = "minioadmin",
    minio_secure: bool = False
):
    job_id = job_payload.get("job_id", "job_demo")
    model_name = job_payload.get("model_name", "bert-base-uncased")
    dataset_name = job_payload.get("dataset_name", "wnut_17")
    epochs = job_payload.get("epochs", 1)
    batch_size = job_payload.get("batch_size", 8)
    learning_rate = job_payload.get("learning_rate", 5e-5)

    work_dir = f"/tmp/training_jobs/{job_id}"
    os.makedirs(work_dir, exist_ok=True)
    log_file_path = os.path.join(work_dir, "training.log")
    
    logger = setup_logger(log_file_path)
    logger.info(f"========== Starting Job {job_id} ==========")
    logger.info(f"Model: {model_name} | Dataset: {dataset_name} | Epochs: {epochs} | Batch Size: {batch_size}")
    
    # Check GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Training Device: {device} (CUDA Available: {torch.cuda.is_available()})")
    if torch.cuda.is_available():
        logger.info(f"GPU Name: {torch.cuda.get_device_name(0)}")

    # MinIO Client
    minio_client = Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=minio_secure
    )

    # 1. Download Dataset from MinIO
    local_data_dir = os.path.join(work_dir, "dataset")
    downloaded_files = download_dataset_from_minio(minio_client, dataset_name, local_data_dir, logger)
    raw_datasets = load_local_jsonl_dataset(downloaded_files)
    logger.info(f"Dataset Loaded Successfully: {raw_datasets}")

    # 2. Extract NER Tags / Labels
    # ใน WNUT_17 มี ner_tags
    if "train" in raw_datasets and "ner_tags" in raw_datasets["train"].features:
        label_list = ["O", "B-corporation", "I-corporation", "B-creative-work", "I-creative-work", 
                      "B-group", "I-group", "B-location", "I-location", "B-person", "I-person", "B-product", "I-product"]
    else:
        label_list = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"]
        
    id2label = {i: label for i, label in enumerate(label_list)}
    label2id = {label: i for i, label in enumerate(label_list)}

    # 3. Tokenizer & Token Alignment (Ref: HF Course Chapter 7)
    logger.info(f"Loading Tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(
            examples["tokens"],
            truncation=True,
            is_split_into_words=True
        )
        labels = []
        for i, label in enumerate(examples["ner_tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)
                elif word_idx != previous_word_idx:
                    label_ids.append(label[word_idx] if word_idx < len(label) else -100)
                else:
                    label_ids.append(label[word_idx] if word_idx < len(label) else -100)
                previous_word_idx = word_idx
            labels.append(label_ids)
        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    logger.info("Tokenizing and aligning dataset labels...")
    tokenized_datasets = raw_datasets.map(tokenize_and_align_labels, batched=True)

    # 4. Load Model
    logger.info(f"Loading Model: {model_name} with num_labels={len(label_list)}")
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id
    )

    output_model_dir = os.path.join(work_dir, "saved_model")
    training_args = TrainingArguments(
        output_dir=output_model_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        eval_strategy="no",
        save_strategy="no",
        logging_steps=10,
        use_cpu=not torch.cuda.is_available()
    )

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    # 5. Execute Training
    print(f"[Trainer Worker] Starting Training loop for job {job_id}...", flush=True)
    logger.info("Starting Training loop...")
    train_result = trainer.train()
    print(f"[Trainer Worker] Training loop complete! Result: {train_result.metrics}", flush=True)
    logger.info(f"Training Complete! Metrics: {train_result.metrics}")
    
    # Save Model & Tokenizer locally
    print(f"[Trainer Worker] Saving model locally to {output_model_dir}...", flush=True)
    trainer.save_model(output_model_dir)
    tokenizer.save_pretrained(output_model_dir)
    logger.info(f"Model saved locally at {output_model_dir}")

    # 6. Upload Saved Model & Logs to MinIO
    models_bucket = "models"
    print(f"[Trainer Worker] Connecting to MinIO to upload artifacts to bucket '{models_bucket}'...", flush=True)
    if not minio_client.bucket_exists(models_bucket):
        print(f"[Trainer Worker] Creating bucket '{models_bucket}' in MinIO...", flush=True)
        minio_client.make_bucket(models_bucket)

    minio_prefix = f"token-classification/{job_id}"
    logger.info(f"Uploading trained model artifacts to MinIO bucket '{models_bucket}' prefix '{minio_prefix}'...")

    for root, dirs, files in os.walk(output_model_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, output_model_dir)
            minio_object_name = f"{minio_prefix}/{rel_path}".replace("\\", "/")
            
            print(f"[Trainer Worker] Uploading artifact: {minio_object_name} ({os.path.getsize(local_path)} bytes)...", flush=True)
            logger.info(f"Uploading artifact: {minio_object_name}")
            minio_client.fput_object(models_bucket, minio_object_name, local_path)

    # Upload training.log
    log_object_name = f"{minio_prefix}/training.log"
    print(f"[Trainer Worker] Uploading log: {log_object_name}...", flush=True)
    minio_client.fput_object(models_bucket, log_object_name, log_file_path)
    logger.info(f"Uploaded training log to MinIO: {models_bucket}/{log_object_name}")
    print(f"[Trainer Worker] ========== Job {job_id} Finished Successfully ==========", flush=True)
    logger.info(f"========== Job {job_id} Finished Successfully ==========")

    return {
        "status": "success",
        "job_id": job_id,
        "minio_model_path": f"{models_bucket}/{minio_prefix}/"
    }
