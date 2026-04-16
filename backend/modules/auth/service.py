import random
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from modules.auth.models import User, OTP
from modules.auth.schemas import SignupRequest, LoginRequest, RequestOTP, VerifyOTP

logger = logging.getLogger(__name__)

class AuthService:
    def _send_email(self, to_email: str, subject: str, body: str):
        if settings.smtp_email and settings.smtp_password:
            try:
                msg = EmailMessage()
                msg.set_content(body)
                msg['Subject'] = subject
                msg['From'] = settings.smtp_email
                msg['To'] = to_email

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(settings.smtp_email, settings.smtp_password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Successfully sent OTP email to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email to {to_email}: {e}")
                # We won't block the request, we'll just log it and fallback to mock if needed
                return False
        else:
            logger.info("\n" + "=" * 40)
            logger.info(f"MOCK EMAIL TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"BODY:\n{body}")
            logger.info("=" * 40 + "\n")
            return True

    async def request_otp(self, db: AsyncSession, payload: RequestOTP):
        # Check if email is already a verified user
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if user and user.is_verified:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Generate 6-digit OTP
        otp_code = f"{random.randint(0, 999999):06d}"
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        # Remove old OTPs for this email
        await db.execute(delete(OTP).where(OTP.email == payload.email))
        
        # Save new OTP
        db_otp = OTP(email=payload.email, otp=otp_code, expires_at=expires_at)
        db.add(db_otp)
        await db.commit()

        # Send OTP
        subject = "Your Verification Code"
        body = f"Hello {payload.name},\n\nYour 6-digit OTP for signup is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nThank you!"
        self._send_email(payload.email, subject, body)

        return {"message": "OTP sent successfully (check server logs if SMTP is not configured)"}

    async def verify_otp(self, db: AsyncSession, payload: VerifyOTP):
        result = await db.execute(select(OTP).where(OTP.email == payload.email))
        db_otp = result.scalar_one_or_none()

        if not db_otp:
            raise HTTPException(status_code=400, detail="No OTP found for this email")
        
        if datetime.utcnow() > db_otp.expires_at:
            await db.execute(delete(OTP).where(OTP.email == payload.email))
            await db.commit()
            raise HTTPException(status_code=400, detail="OTP has expired")
            
        if db_otp.otp != payload.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        return {"verified": True}

    async def signup(self, db: AsyncSession, payload: SignupRequest):
        # Verify OTP
        await self.verify_otp(db, VerifyOTP(email=payload.email, otp=payload.otp))

        # Check if user exists
        result = await db.execute(select(User).where(User.email == payload.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create User
        hashed_pw = get_password_hash(payload.password)
        user_id = str(uuid4())
        
        new_user = User(
            id=user_id,
            name=payload.name,
            email=payload.email,
            hashed_password=hashed_pw,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(new_user)

        # Delete OTP
        await db.execute(delete(OTP).where(OTP.email == payload.email))
        await db.commit()
        await db.refresh(new_user)
        
        return new_user

    async def login(self, db: AsyncSession, payload: LoginRequest):
        # Look up user by email
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=400, detail="No account found")
            
        if not user.is_verified:
            raise HTTPException(status_code=400, detail="Account not verified")

        # Verify password
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Generate JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "name": user.name, "id": user.id}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

auth_service = AuthService()
