# Assignment WTN-A09: Observability Tools for AI Ecosystem

## สิ่งที่ทำไป
* **ติดตั้งและบูรณาการ Observability Stack ครบทั้ง 5 ตัว (The LGTM + OTel Stack)**:
  - **OpenTelemetry (OTel Collector)**: ทำหน้าที่เป็นศูนย์กลางรับ Traces ผ่าน OTLP gRPC (`:4317`) และ HTTP (`:4318`) แล้วส่งต่อไปยัง Tempo
  - **Prometheus**: ทำหน้าที่เป็น Time-Series DB ดึงและจัดเก็บค่าสถิติ (Metrics) จาก `/metrics` ของ FastAPI และ OTel Collector
  - **Loki & Promtail**: รวบรวมและสตรีม Log ข้อความจาก Docker Containers ทั้งหมดในระบบ (FastAPI, Workers, MLflow, MinIO) เข้าสู่ศูนย์กลางแบบเรียลไทม์
  - **Tempo**: จัดเก็บและสืบค้น Distributed Tracing เพื่อติดตามเส้นทางการทำงานของคำขอแบบ End-to-End
  - **Grafana**: หน้าจอแสดงผลศูนย์กลาง (Single Pane of Glass) ที่รวมทั้ง Metrics, Logs, และ Traces ไว้ในแดชบอร์ดเดียว
* **สร้างระบบ Instrumentation ใน FastAPI และ Inference Service**:
  - ติดตั้ง Prometheus Exporter ใน `main.py` สำหรับเปิด Endpoint `/metrics`
  - พัฒนา OpenTelemetry HTTP Tracing Middleware เพื่อสร้าง Spans ของทุกคำขอ API
  - เพิ่ม Custom Trace Spans ใน `mlflow_service.py` สำหรับติดตามเวลาการโหลดโมเดล (`mlflow.load_model`) และการประมวลผลคำศัพท์ (`ner.token_classification`)



## Added & Modified Files
* `observability/prometheus/prometheus.yml`: ตั้งค่า Scrape Targets สำหรับ FastAPI Backend และ OTel Collector
* `observability/loki/loki-config.yml`: ตั้งค่า Local Storage, Compactor และ Schema ของ Loki
* `observability/promtail/promtail-config.yml`: ตั้งค่า Promtail ดึง Log จาก Docker Socket ส่งเข้า Loki
* `observability/tempo/tempo.yml`: ตั้งค่าการรับ Traces ผ่าน OTLP และพื้นที่จัดเก็บ Traces
* `observability/otel-collector/otel-collector-config.yml`: ตั้งค่า Pipeline รับ OTLP Spans แล้วส่งออกไปยัง Tempo และ Prometheus
* `observability/grafana/provisioning/datasources/datasources.yml`: กำหนด Data Sources ให้ Grafana เชื่อมโยง Prometheus, Loki, และ Tempo แบบอัตโนมัติ
* `observability/grafana/provisioning/dashboards/dashboards.yml`: ตั้งค่า Dashboard Provisioning สำหรับ Grafana
* `backend/Dockerfile`: ติดตั้งไลบรารี `prometheus-fastapi-instrumentator` และ OpenTelemetry SDK
* `backend/main.py`: ติดตั้ง OpenTelemetry Tracing Middleware และเปิด Endpoint `/metrics`
* `backend/services/mlflow_service.py`: ห่อหุ้มฟังก์ชันทำนายผลและโหลดโมเดลด้วย OpenTelemetry Spans
* `compose.yml`: เพิ่ม 6 Services ใหม่อย่างสมบูรณ์ (`otel_collector`, `prometheus`, `loki`, `promtail`, `tempo`, `grafana`) พร้อมกำหนด Volumes

