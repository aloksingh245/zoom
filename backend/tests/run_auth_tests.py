import asyncio
import logging
from datetime import datetime, timedelta
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from main import app
from core.database import Base
from core.database import engine as default_engine
from modules.auth.models import OTP, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_tests():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    from core.database import get_db
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)
    
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
            
    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Request OTP
        email = "testuser@example.com"
        res = await client.post("/api/auth/request-otp", json={"name": "Test User", "email": email})
        assert res.status_code == 200, f"Request OTP failed: {res.text}"
        print("✅ OTP requested successfully.")
        
        async with TestSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(OTP).where(OTP.email == email))
            otp_record = result.scalar_one_or_none()
            assert otp_record is not None, "OTP not saved in DB"
            otp_code = otp_record.otp
            print(f"✅ OTP generated and stored in DB: {otp_code}")

        # Test 2: Verify OTP with WRONG code (Edge Case)
        res = await client.post("/api/auth/signup", json={
            "name": "Test User", "email": email, "otp": "000000", "password": "password123"
        })
        assert res.status_code == 400 and "Invalid OTP" in res.text, "Failed to catch invalid OTP"
        print("✅ Edge Case: Invalid OTP rejected.")

        # Test 3: Verify EXPIRED OTP (Edge Case)
        async with TestSessionLocal() as session:
            result = await session.execute(select(OTP).where(OTP.email == email))
            otp_record = result.scalar_one_or_none()
            # Manually expire the OTP
            otp_record.expires_at = datetime.utcnow() - timedelta(minutes=5)
            session.add(otp_record)
            await session.commit()
            
        res = await client.post("/api/auth/signup", json={
            "name": "Test User", "email": email, "otp": otp_code, "password": "password123"
        })
        assert res.status_code == 400 and "OTP has expired" in res.text, "Failed to catch expired OTP"
        print("✅ Edge Case: Expired OTP rejected.")

        # Test 4: Request new OTP (Overwrite old)
        res = await client.post("/api/auth/request-otp", json={"name": "Test User", "email": email})
        assert res.status_code == 200
        async with TestSessionLocal() as session:
            result = await session.execute(select(OTP).where(OTP.email == email))
            otp_record = result.scalar_one_or_none()
            new_otp_code = otp_record.otp
        print(f"✅ Requested new OTP: {new_otp_code}")

        # Test 5: Successful Signup
        res = await client.post("/api/auth/signup", json={
            "name": "Test User", "email": email, "otp": new_otp_code, "password": "password123"
        })
        assert res.status_code == 200, f"Signup failed: {res.text}"
        print("✅ Signup successful.")

        # Test 6: Request OTP for existing user (Edge Case)
        res = await client.post("/api/auth/request-otp", json={"name": "Test User", "email": email})
        assert res.status_code == 400 and "Email already registered" in res.text
        print("✅ Edge Case: Prevent OTP request for already registered user.")

        # Test 7: Login with wrong password (Edge Case)
        res = await client.post("/api/auth/login", json={"email": email, "password": "wrongpassword"})
        assert res.status_code == 400 and "Invalid credentials" in res.text
        print("✅ Edge Case: Login with wrong password rejected.")

        # Test 8: Login with non-existent email (Edge Case)
        res = await client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password123"})
        assert res.status_code == 400 and "No account found" in res.text
        print("✅ Edge Case: Login with non-existent email rejected.")

        # Test 9: Successful Login
        res = await client.post("/api/auth/login", json={"email": email, "password": "password123"})
        assert res.status_code == 200, f"Login failed: {res.text}"
        data = res.json()
        assert "access_token" in data
        print(f"✅ Login successful. Received JWT Token: {data['access_token'][:15]}...")
        
    await test_engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_tests())