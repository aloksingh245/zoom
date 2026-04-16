import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app
from core.database import Base, get_db
from modules.auth.models import User, OTP

async def test_duplicate_email():
    # 1. Setup fresh in-memory test database
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)
    
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
            
    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        email = "duplicate@example.com"
        
        print(f"\n--- Testing Duplicate Email Protection for: {email} ---")

        # Step 1: Successful First Signup
        # Request OTP
        await client.post("/api/auth/request-otp", json={"name": "First User", "email": email})
        
        # Get the OTP from DB
        async with TestSessionLocal() as session:
            from sqlalchemy import select
            res = await session.execute(select(OTP).where(OTP.email == email))
            otp_code = res.scalar_one().otp
        
        # Complete Signup
        signup_res = await client.post("/api/auth/signup", json={
            "name": "First User", "email": email, "otp": otp_code, "password": "password123"
        })
        print(f"1. First Signup: {signup_res.status_code} OK")

        # Step 2: Try to request OTP for the SAME email again
        otp_retry_res = await client.post("/api/auth/request-otp", json={"name": "Second User", "email": email})
        print(f"2. Requesting OTP for same email again: {otp_retry_res.status_code}")
        print(f"   Response: {otp_retry_res.json()}")
        
        # Step 3: Try to force a signup for the SAME email (Edge case: bypass OTP check logic)
        # Even if someone calls the signup endpoint directly with a guessed/old OTP
        force_signup_res = await client.post("/api/auth/signup", json={
            "name": "Second User", "email": email, "otp": "000000", "password": "password456"
        })
        print(f"3. Forced Signup attempt for same email: {force_signup_res.status_code}")
        print(f"   Response: {force_signup_res.json()}")

    await test_engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_duplicate_email())
