from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.auth import schemas
from modules.auth.service import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/request-otp")
async def request_otp(payload: schemas.RequestOTP, db: AsyncSession = Depends(get_db)):
    return await auth_service.request_otp(db, payload)

@router.post("/signup", response_model=schemas.UserResponse)
async def signup(payload: schemas.SignupRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.signup(db, payload)

@router.post("/login")
async def login(payload: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, payload)
