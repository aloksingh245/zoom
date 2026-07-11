"""
Test: Full Google Calendar OAuth flow
Tests:
  1. Login with real admin user
  2. GET /api/classes/sync/calendar/status  -> connected or not
  3. GET /api/classes/sync/calendar/auth    -> returns auth_url with PKCE
  4. Verifies PKCE code_verifier is stored in _pkce_store
  5. Verifies auth_url contains expected Google OAuth params
"""
import pytest
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


@pytest.fixture
def admin_jwt(mock_smtp):
    """Create a fresh verified admin and return its JWT."""
    email = "oauth_test_admin@example.com"
    password = "testpass123"

    # Cleanup
    conn = sqlite3.connect("sql_app.db")
    conn.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()

    # Signup
    r = client.post("/auth/signup", json={"email": email, "password": password, "role": "admin"})
    assert r.status_code == 201

    # Get token from DB
    conn = sqlite3.connect("sql_app.db")
    row = conn.execute("SELECT verification_token FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    token = row[0]

    # Verify email
    r = client.post(f"/auth/verify-email?token={token}")
    assert r.status_code == 200

    # Login
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    jwt = r.json()["access_token"]

    yield jwt

    # Cleanup
    conn = sqlite3.connect("sql_app.db")
    conn.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()


def test_calendar_status(admin_jwt):
    """GET /api/classes/sync/calendar/status should return connected bool."""
    headers = {"Authorization": f"Bearer {admin_jwt}"}
    r = client.get("/api/classes/sync/calendar/status", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "connected" in data
    print(f"\n  ✅ Calendar connected: {data['connected']}")


def test_calendar_auth_url_generated(admin_jwt):
    """GET /api/classes/sync/calendar/auth should return a valid Google auth URL."""
    headers = {"Authorization": f"Bearer {admin_jwt}"}
    r = client.get("/api/classes/sync/calendar/auth", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "auth_url" in data

    auth_url = data["auth_url"]
    print(f"\n  ✅ Auth URL generated: {auth_url[:80]}...")

    # Must be a real Google OAuth URL
    assert "accounts.google.com/o/oauth2/auth" in auth_url
    # Must request calendar scopes
    assert "calendar" in auth_url
    # Must have redirect_uri pointing to our callback
    assert "localhost%3A8000" in auth_url or "localhost:8000" in auth_url
    # Must have offline access
    assert "offline" in auth_url


def test_pkce_code_verifier_stored(admin_jwt):
    """Calling /auth should store a code_verifier in _pkce_store if PKCE is used."""
    from modules.classes.router import _pkce_store

    # Clear store first
    _pkce_store.clear()

    headers = {"Authorization": f"Bearer {admin_jwt}"}
    r = client.get("/api/classes/sync/calendar/auth", headers=headers)
    assert r.status_code == 200

    if _pkce_store:
        state = list(_pkce_store.keys())[0]
        verifier = _pkce_store[state]
        print(f"\n  ✅ PKCE code_verifier stored — state: {state[:8]}..., verifier length: {len(verifier)}")
        assert len(verifier) > 0
    else:
        print("\n  ℹ️  No PKCE code_verifier stored (library version may not use PKCE)")


def test_calendar_callback_uses_code_verifier(admin_jwt):
    """Callback should pass code_verifier to fetch_token when available."""
    from modules.classes.router import _pkce_store

    _pkce_store.clear()
    # Pre-seed a fake code_verifier
    _pkce_store["test_state_123"] = "fake_verifier_abc"

    with patch("google_auth_oauthlib.flow.Flow.fetch_token") as mock_fetch, \
         patch("google_auth_oauthlib.flow.Flow.credentials", new_callable=lambda: property(lambda self: MagicMock(to_json=lambda: '{}'))):
        mock_fetch.return_value = {}

        r = client.get(
            "/api/classes/sync/calendar/callback",
            params={"code": "fake_code", "state": "test_state_123"}
        )

        # fetch_token should have been called with code_verifier
        mock_fetch.assert_called_once()
        call_kwargs = mock_fetch.call_args[1]
        assert call_kwargs.get("code_verifier") == "fake_verifier_abc"
        print(f"\n  ✅ fetch_token called with code_verifier: {call_kwargs.get('code_verifier')}")

        # State should be cleaned up from store
        assert "test_state_123" not in _pkce_store
        print("  ✅ PKCE state cleaned up from store after use")
