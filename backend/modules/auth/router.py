from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import uuid4
from core.database import get_db
from modules.auth import models, schemas, utils
from modules.auth.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

async def background_calendar_sync():
    """Background task to sync the calendar with Google Calendar on successful admin login."""
    from core.database import async_session_factory
    from modules.classes.service import class_service
    from integrations.google_calendar.client import calendar_service
    import asyncio
    
    # 1. Check if calendar is authenticated (credentials exist)
    try:
        creds = await asyncio.to_thread(calendar_service._get_credentials)
        if not creds:
            logger.info("Google Calendar not authenticated/connected. Skipping auto-sync on login.")
            return
    except Exception as e:
        logger.error(f"Error checking Google Calendar credentials: {e}")
        return

    logger.info("Starting background Google Calendar sync on login...")
    try:
        async with async_session_factory() as db:
            result = await class_service.sync_with_calendar(db)
            logger.info(f"Background Google Calendar sync completed successfully: {result}")
    except Exception as exc:
        logger.error(f"Error executing background calendar sync: {exc}")

@router.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def signup(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if user already exists
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # 2. Create the user
    hashed_pwd = utils.hash_password(payload.password)
    verification_token = str(uuid4())
    
    db_user = models.User(
        email=payload.email,
        hashed_password=hashed_pwd,
        role=payload.role or "admin",
        is_verified=False,
        verification_token=verification_token
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # 3. Send verification email (or mock to log)
    utils.send_verification_email(db_user.email, verification_token)

    return db_user

@router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.verification_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token."
        )

    user.is_verified = True
    user.verification_token = None
    await db.commit()

    return {"message": "Email verified successfully! You can now log in."}

@router.post("/login", response_model=schemas.Token)
async def login(
    payload: schemas.UserLogin,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    user = result.scalar_one_or_none()
    
    if not user or not utils.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in."
        )

    # Generate JWT
    access_token = utils.create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    # Auto-sync Google Calendar in background on admin login
    if user.role == "admin":
        background_tasks.add_task(background_calendar_sync)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

from datetime import datetime, timedelta

@router.post("/forgot-password")
async def forgot_password(payload: schemas.ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # 1. Look up user by email
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    user = result.scalar_one_or_none()
    
    # 2. If user exists, create token & expires date, save and email
    if user:
        reset_token = str(uuid4())
        user.reset_token = reset_token
        # Token valid for 15 minutes
        user.reset_token_expires = datetime.utcnow() + timedelta(minutes=15)
        await db.commit()
        
        utils.send_reset_password_email(user.email, reset_token)
        
    # Always return a success response to avoid email enumeration attacks
    return {"message": "If your email is registered, we have sent a reset password link to it."}

@router.post("/reset-password")
async def reset_password(payload: schemas.ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # 1. Retrieve user with active token
    result = await db.execute(
        select(models.User)
        .where(models.User.reset_token == payload.token)
    )
    user = result.scalar_one_or_none()
    
    # 2. Validate token presence & expiration
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token."
        )
        
    # 3. Hash new password and clear token columns
    user.hashed_password = utils.hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
    
    return {"message": "Password reset successful! You can now log in with your new password."}

@router.get("/users/stats")
async def get_users_stats(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    student_res = await db.execute(select(func.count(models.User.id)).where(models.User.role == "student"))
    student_count = student_res.scalar() or 0
    
    mentor_res = await db.execute(select(func.count(models.User.id)).where(models.User.role == "mentor"))
    mentor_count = mentor_res.scalar() or 0
    
    total_res = await db.execute(select(func.count(models.User.id)))
    total_count = total_res.scalar() or 0
    
    return {
        "students": student_count,
        "mentors": mentor_count,
        "total": total_count
    }

