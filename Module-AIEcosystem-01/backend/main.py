"""
FastAPI Application Entry Point
ทำหน้าที่ประกอบส่วนประกอบต่างๆ (Routers, Database Tables, Global Middleware) เข้าด้วยกัน
ตามหลักการ Layered Architecture และ Separation of Concerns (SoC)
"""

import os
from fastapi import FastAPI
from core.config import settings
from core.database import engine, Base
from api.v1.auth_router import router as auth_router
from api.v1.training_router import router as training_router
from api.v1.inference_router import router as inference_router

# OpenTelemetry & Prometheus Observability Libraries
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# นำเข้า Models เพื่อให้ SQLAlchemy รู้จัก Schema ตารางในการ auto-create
import models.user  # noqa: F401

# สร้างตารางใน Database หากยังไม่มี (สำหรับ Production แนะนำให้ใช้ Alembic)
Base.metadata.create_all(bind=engine)

# สร้าง FastAPI Application Instance
app = FastAPI(
    title=settings.app_name,
    description="""
    ## AI Ecosystem Authentication, Model Training & Inference API Service
    ระบบ API พัฒนาตามแนวทาง **Separation of Concerns (SoC)**
    และ **Layered Architecture** สำหรับจัดการระบบสมาชิก, **Delayed Training Task Queue** และ **MLflow Model Inference**
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# OpenTelemetry Distributed Tracing Setup
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector:4317")
try:
    resource = Resource.create({"service.name": "fastapi_backend"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    print(f"[OpenTelemetry] Tracing initialized -> OTLP: {OTEL_ENDPOINT}")
except Exception as e:
    print(f"[OpenTelemetry] Provider setup note: {e}")

tracer = trace.get_tracer("fastapi_backend")

@app.middleware("http")
async def trace_requests_middleware(request, call_next):
    """OpenTelemetry HTTP Tracing Middleware to generate spans for Tempo"""
    span_name = f"{request.method} {request.url.path}"
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.route", request.url.path)
        try:
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)
            return response
        except Exception as exc:
            span.record_exception(exc)
            raise exc

# Prometheus Metrics Exporter (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ลงทะเบียน Router โดยแบ่งตาม Domain และ Versioning (/api/v1/auth, /api/v1/training, /api/v1/inference)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(training_router, prefix="/api/v1")
app.include_router(inference_router, prefix="/api/v1")


@app.get("/", tags=["System"])
def root():
    return {
        "app": settings.app_name,
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Monitoring API: Health Check Endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
