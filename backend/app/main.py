from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.router import router
from .db.database import engine, Base

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# Initialize database on startup
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok", "app_name": settings.app_name, "version": settings.app_version}
