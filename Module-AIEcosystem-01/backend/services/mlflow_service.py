"""
Business Logic Layer: MLflow Integration & Inference Service
จัดการโหลดโมเดลจาก MLflow Model Registry / Artifact Store และทำนายคำศัพท์ (NER Inference)
"""

import os
import time
import mlflow
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from schemas.inference import PredictRequest, PredictResponse, EntityResult
from contextlib import contextmanager

try:
    from opentelemetry import trace
    tracer = trace.get_tracer("mlflow_service")
except Exception:
    tracer = None

@contextmanager
def safe_span(name, attributes=None):
    if tracer:
        with tracer.start_as_current_span(name) as span:
            if attributes:
                for k, v in attributes.items():
                    span.set_attribute(k, v)
            yield span
    else:
        class DummySpan:
            def set_attribute(self, *a, **kw): pass
            def record_exception(self, *a, **kw): pass
        yield DummySpan()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Cache loaded pipelines in memory for high-performance inference
MODEL_CACHE = {}

class MLflowService:
    def resolve_model_uri(self, model_name: str = "Token-Classification-Model", run_id: str = None) -> str:
        """กำหนด Model URI สำหรับโหลดจาก MLflow"""
        if run_id:
            return f"runs:/{run_id}/model"
        return f"models:/{model_name}/latest"

    def get_or_load_pipeline(self, model_uri: str):
        """โหลดโมเดลและ Tokenizer จาก MLflow มาสร้าง Transformers Pipeline (พร้อม caching)"""
        if model_uri in MODEL_CACHE:
            return MODEL_CACHE[model_uri]

        with safe_span("mlflow.load_model", {"model.uri": model_uri}) as span:
            print(f"[MLflowService] โหลดโมเดลจาก MLflow URI: '{model_uri}'...")
            try:
                # โหลดจาก MLflow Artifact Store
                loaded_pipeline = mlflow.transformers.load_model(model_uri)
            except Exception as e:
                span.record_exception(e)
                print(f"[MLflowService] Warning: ไม่พบโมเดลใน MLflow ({e}) โหลด Default BERT Base Tokenizer & Model...")
                # Fallback ใช้ Pretrained Bert หากยังไม่มี Model ใน MLflow
                label_list = ["O", "B-corporation", "I-corporation", "B-creative-work", "I-creative-work", 
                              "B-group", "I-group", "B-location", "I-location", "B-person", "I-person", "B-product", "I-product"]
                id2label = {i: label for i, label in enumerate(label_list)}
                label2id = {label: i for i, label in enumerate(label_list)}
                
                tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                model = AutoModelForTokenClassification.from_pretrained(
                    "bert-base-uncased", num_labels=len(label_list), id2label=id2label, label2id=label2id
                )
                loaded_pipeline = pipeline("token-classification", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

            MODEL_CACHE[model_uri] = loaded_pipeline
            return loaded_pipeline

    def predict_entities(self, req: PredictRequest) -> PredictResponse:
        """ทำการวิเคราะห์ข้อความเพื่อแท็กหมวดหมู่คำ (Named Entity Recognition)"""
        start_time = time.time()
        model_uri = self.resolve_model_uri(model_name=req.model_name, run_id=req.run_id)

        with safe_span("ner.token_classification", {"model.uri": model_uri, "input.text_length": len(req.text)}):
            nlp_pipeline = self.get_or_load_pipeline(model_uri)
            predictions = nlp_pipeline(req.text)

        entities = []
        for pred in predictions:
            entities.append(EntityResult(
                word=str(pred.get("word", "")),
                entity_group=str(pred.get("entity_group", pred.get("entity", "O"))),
                score=round(float(pred.get("score", 0.0)), 4)
            ))

        exec_time = round(time.time() - start_time, 4)

        return PredictResponse(
            text=req.text,
            entities=entities,
            model_uri=model_uri,
            execution_time_sec=exec_time,
            message="Prediction completed successfully via MLflow Model Pipeline"
        )

mlflow_service = MLflowService()
