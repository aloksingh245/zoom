import pytest
from fastapi.testclient import TestClient
import sqlite3
from main import app

client = TestClient(app)

def test_auth_full_flow():
    email = "testauthuser@example.com"
    signup_payload = {
        "email": email,
        "password": "strongpassword123",
        "role": "admin"
    }
    
    # Clean database before running
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()

    # 1. Sign up
    response = client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "admin"
    assert data["is_verified"] is False
    
    # Retrieve token directly from DB for verification
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT verification_token FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    token = row[0]
    assert token is not None

    # 2. Login fails before email is verified
    login_payload = {
        "email": email,
        "password": "strongpassword123"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 403
    assert "verify your email" in response.json()["detail"].lower()

    # 3. Verify Email
    response = client.post(f"/auth/verify-email?token={token}")
    assert response.status_code == 200
    assert "verified" in response.json()["message"].lower()

    # 4. Login succeeds after verification
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # 5. Access /auth/me with JWT token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["email"] == email
    assert me_data["is_verified"] is True

    # Access /auth/users/stats with JWT token
    response = client.get("/auth/users/stats", headers=headers)
    assert response.status_code == 200
    stats_data = response.json()
    assert "students" in stats_data
    assert "mentors" in stats_data
    assert "total" in stats_data
    
    # 6. Clean database after running
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()
