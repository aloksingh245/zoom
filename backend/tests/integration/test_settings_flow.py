import pytest
from fastapi.testclient import TestClient
import sqlite3
import os
import shutil
from main import app
from core.config import settings

client = TestClient(app)

# Fixture to safely backup and restore the .env file during settings tests
@pytest.fixture(autouse=True)
def manage_env_backup():
    # Resolve .env paths relative to backend root (two levels up from tests/integration)
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env_path = os.path.join(backend_root, ".env")
    backup_path = os.path.join(backend_root, ".env.bak")
    
    # Create backup if .env exists
    has_env = os.path.exists(env_path)
    if has_env:
        shutil.copy2(env_path, backup_path)
        
    yield
    
    # Restore backup and delete it
    if has_env:
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, env_path)
            os.remove(backup_path)
    elif os.path.exists(env_path):
        os.remove(env_path)

def test_settings_flow():
    admin_email = "settingsadmin@example.com"
    mentor_email = "settingsmentor@example.com"
    
    # Cleanup database from any stale test users
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email IN (?, ?)", (admin_email, mentor_email))
    conn.commit()
    conn.close()

    # 1. Access settings anonymously -> 401 Unauthorized
    resp = client.get("/api/settings")
    assert resp.status_code == 401

    # 2. Create users (one admin, one mentor)
    # Admin Signup
    resp = client.post("/auth/signup", json={
        "email": admin_email,
        "password": "strongadminpwd123",
        "role": "admin"
    })
    assert resp.status_code == 201
    
    # Mentor Signup
    resp = client.post("/auth/signup", json={
        "email": mentor_email,
        "password": "strongmentorpwd123",
        "role": "mentor"
    })
    assert resp.status_code == 201

    # Retrieve verification tokens directly from SQLite DB
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT verification_token, role FROM users WHERE email=?", (admin_email,))
    admin_token = cursor.fetchone()[0]
    cursor.execute("SELECT verification_token, role FROM users WHERE email=?", (mentor_email,))
    mentor_token = cursor.fetchone()[0]
    conn.close()

    # Verify both emails
    resp = client.post(f"/auth/verify-email?token={admin_token}")
    assert resp.status_code == 200
    resp = client.post(f"/auth/verify-email?token={mentor_token}")
    assert resp.status_code == 200

    # Log in both users and extract access tokens
    resp = client.post("/auth/login", json={"email": admin_email, "password": "strongadminpwd123"})
    assert resp.status_code == 200
    admin_jwt = resp.json()["access_token"]

    resp = client.post("/auth/login", json={"email": mentor_email, "password": "strongmentorpwd123"})
    assert resp.status_code == 200
    mentor_jwt = resp.json()["access_token"]

    # 3. Access settings as mentor -> 403 Forbidden
    headers_mentor = {"Authorization": f"Bearer {mentor_jwt}"}
    resp = client.get("/api/settings", headers=headers_mentor)
    assert resp.status_code == 403

    resp = client.post("/api/settings", headers=headers_mentor, json={"smtp_port": 12345})
    assert resp.status_code == 403

    # 4. Access settings as admin -> 200 OK
    headers_admin = {"Authorization": f"Bearer {admin_jwt}"}
    resp = client.get("/api/settings", headers=headers_admin)
    assert resp.status_code == 200
    settings_data = resp.json()
    assert "smtp_port" in settings_data
    assert "timezone_default" in settings_data

    # 5. Update settings as admin -> 200 OK
    # Save original app_url to test updating it
    original_app_url = settings_data.get("app_url", "http://localhost:5173")
    new_app_url = "http://test-url-endpoint.com"

    update_payload = {
        "zoom_account_id": "test_account_id",
        "zoom_client_id": "test_client_id",
        "zoom_client_secret": "••••••••", # Should be ignored because it is placeholder
        "zoom_user_id": "test_user@example.com",
        "google_calendar_id": "primary",
        "google_sheet_id": "sheet_id_123",
        "smtp_host": "smtp.test.com",
        "smtp_port": 9876,
        "smtp_username": "smtp_user",
        "smtp_password": "••••••••", # Should be ignored because it is placeholder
        "smtp_from": "test_smtp@example.com",
        "app_url": new_app_url,
        "timezone_default": "UTC",
        "gemini_api_key": "test_gemini_key"
    }

    resp = client.post("/api/settings", headers=headers_admin, json=update_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # Verify backend/.env was updated correctly
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env_path = os.path.join(backend_root, ".env")
    with open(env_path, "r") as f:
        env_content = f.read()

    assert "SMTP_PORT=9876" in env_content
    assert "APP_URL=http://test-url-endpoint.com" in env_content
    assert "TIMEZONE_DEFAULT=UTC" in env_content
    assert "GEMINI_API_KEY=test_gemini_key" in env_content
    
    # Confirm secrets masked as "••••••••" were ignored and not written literally
    assert "••••••••" not in env_content

    # 6. Cleanup DB after runs
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email IN (?, ?)", (admin_email, mentor_email))
    conn.commit()
    conn.close()
