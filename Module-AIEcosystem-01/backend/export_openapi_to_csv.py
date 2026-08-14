"""
OpenAPI JSON to CSV / Excel Converter Script
สำหรับ Snapshot รายการ API ทั้งหมดในระบบ FastAPI เป็นไฟล์ CSV / Excel (CSV with UTF-8 BOM for Excel compatibility)

อ้างอิงโจทย์ข้อ 3e: แปลง openapi.json เป็น Excel หรือ CSV สำหรับ Snapshot API List ของระบบ
"""

import json
import csv
import sys
from pathlib import Path

def generate_openapi_csv():
    # ดึง OpenAPI Schema โดยตรงจาก FastAPI App หรืออ่านจากไฟล์ openapi.json
    try:
        sys.path.append(str(Path(__file__).parent))
        from main import app
        openapi_schema = app.openapi()
    except Exception as e:
        json_path = Path("openapi.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                openapi_schema = json.load(f)
        else:
            print(f"ไม่สามารถโหลด OpenAPI Schema ได้: {e}")
            sys.exit(1)

    # 1. บันทึกเป็นไฟล์ openapi.json Snapshot
    json_output_path = Path("openapi.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    print(f"บันทึกไฟล์ OpenAPI JSON สำเร็จ: {json_output_path.resolve()}")

    # 2. แกะโครงสร้าง API จาก OpenAPI Schema
    rows = []
    paths = openapi_schema.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                continue
            
            tags = ", ".join(details.get("tags", []))
            summary = details.get("summary", "")
            description = details.get("description", "").replace("\n", " ").strip()
            operation_id = details.get("operationId", "")
            
            # รวบรวม HTTP Status Codes ของ Response
            responses = details.get("responses", {})
            status_codes = ", ".join(responses.keys())

            # รวบรวม parameters
            params = details.get("parameters", [])
            param_list = [f"{p.get('name')} ({p.get('in')})" for p in params]
            parameters_str = ", ".join(param_list)

            rows.append({
                "Method": method.upper(),
                "Endpoint Path": path,
                "Tags / Domain": tags,
                "Summary": summary,
                "Description": description,
                "Parameters": parameters_str,
                "Response Codes": status_codes,
                "Operation ID": operation_id
            })

    # 3. บันทึกเป็น CSV (utf-8-sig เพื่อรองรับการเปิดภาษาไทยใน Microsoft Excel ได้โดยตรง)
    csv_output_path = Path("api_snapshot.csv")
    fieldnames = [
        "Method",
        "Endpoint Path",
        "Tags / Domain",
        "Summary",
        "Description",
        "Parameters",
        "Response Codes",
        "Operation ID"
    ]

    with open(csv_output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"แปลงและบันทึก API Snapshot เป็น CSV สำเร็จ: {csv_output_path.resolve()} (รวม {len(rows)} Endpoints)")

if __name__ == "__main__":
    generate_openapi_csv()
