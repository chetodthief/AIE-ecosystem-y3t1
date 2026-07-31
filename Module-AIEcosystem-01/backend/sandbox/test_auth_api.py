"""
Automated Integration Test Script for Authentication API
ทดสอบการทำงานแบบ End-to-End ของทั้ง 4 Layers:
1. POST /api/v1/auth/register (สมัครสมาชิก)
2. POST /api/v1/auth/register (สมัครซ้ำ - ต้องเกิดข้อผิดพลาด 400)
3. POST /api/v1/auth/login (เข้าสู่ระบบ - ได้รับ Tokens)
4. GET /api/v1/auth/me (ดึงข้อมูลผู้ใช้ปัจจุบันด้วย Access Token)
5. POST /api/v1/auth/refresh (ขอ Access Token ใหม่ด้วย Refresh Token)
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Configure stdout encoding to utf-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


from core.database import engine, Base

def test_auth_flow():
    # Reset database tables for clean test state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("=" * 60)
    print("Starting FastAPI Authentication API End-to-End Integration Test")
    print("=" * 60)



    test_user_data = {
        "username": "testuser_ai",
        "email": "testuser@ai-ecosystem.com",
        "password": "SecretPassword123!",
        "full_name": "Test AI Developer"
    }

    # 1. Test Registration
    print("\n--- Step 1: Testing Register Endpoint (POST /api/v1/auth/register) ---")
    response = client.post("/api/v1/auth/register", json=test_user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    registered_data = response.json()
    assert registered_data["username"] == test_user_data["username"]
    assert registered_data["email"] == test_user_data["email"]
    assert "hashed_password" not in registered_data  # Ensure password hash is NOT exposed!
    print("Step 1 Success: User registered successfully.")

    # 2. Test Duplicate Registration (Business logic validation test)
    print("\n--- Step 2: Testing Duplicate Register Error Handling ---")
    dup_response = client.post("/api/v1/auth/register", json=test_user_data)
    print(f"Status Code: {dup_response.status_code}")
    print(f"Response Body: {dup_response.json()}")
    assert dup_response.status_code == 400
    print("Step 2 Success: Duplicate registration properly blocked.")

    # 3. Test Login
    print("\n--- Step 3: Testing Login Endpoint (POST /api/v1/auth/login) ---")
    login_data = {
        "username_or_email": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    print(f"Status Code: {login_response.status_code}")
    print(f"Response Body: {login_response.json()}")
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    print("Step 3 Success: User authenticated and tokens acquired.")

    # 4. Test Protected Endpoint /me with Bearer Token
    print("\n--- Step 4: Testing Protected Me Endpoint (GET /api/v1/auth/me) ---")
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    print(f"Status Code: {me_response.status_code}")
    print(f"Response Body: {me_response.json()}")
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == test_user_data["username"]
    print("Step 4 Success: Protected profile retrieved with JWT token.")

    # 5. Test Refresh Token Endpoint
    print("\n--- Step 5: Testing Refresh Token Endpoint (POST /api/v1/auth/refresh) ---")
    refresh_request = {"refresh_token": refresh_token}
    refresh_response = client.post("/api/v1/auth/refresh", json=refresh_request)
    print(f"Status Code: {refresh_response.status_code}")
    print(f"Response Body: {refresh_response.json()}")
    assert refresh_response.status_code == 200
    new_token_data = refresh_response.json()
    assert "access_token" in new_token_data
    print("Step 5 Success: New access token issued using refresh token.")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! The 4-Layer FastAPI Auth API is fully operational.")
    print("=" * 60)


if __name__ == "__main__":
    test_auth_flow()
