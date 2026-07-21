from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import engine, Base

# Import Routers
from modules.classes.router import router as classes_router
from modules.courses.router import router as courses_router
from integrations.zoom.router import router as zoom_router
from integrations.google_calendar.router import router as calendar_router
from modules.auth.router import router as auth_router
from modules.settings.router import router as settings_router
from modules.super_admin.router import router as super_admin_router

# Import models to ensure they are registered with Base metadata
from modules.auth import models as auth_models
from modules.settings import models as settings_models

# Import Event Listeners to register them
from integrations.google_sheets.listeners import register_listeners as register_sheets_listeners
from integrations.crm.listeners import register_listeners as register_crm_listeners
from modules.agent.listeners import register_listeners as register_agent_listeners
from integrations.email.listeners import register_listeners as register_email_listeners

# Import agent router & RAG initializer
from modules.agent.router import router as agent_router
from modules.agent.agent import initialize_agent_rag

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    # Register Event Listeners
    register_sheets_listeners()
    register_crm_listeners()
    register_agent_listeners()
    register_email_listeners()
    
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed Super Admin
    from core.database import async_session_factory
    from sqlalchemy import select
    from modules.auth.models import User
    from modules.auth.utils import hash_password
    
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == settings.master_admin_username))
        super_admin = result.scalar_one_or_none()
        if not super_admin:
            print(f"Seeding super_admin {settings.master_admin_username}...", flush=True)
            hashed_pwd = hash_password(settings.master_admin_password)
            new_super_admin = User(
                email=settings.master_admin_username,
                hashed_password=hashed_pwd,
                role="super_admin",
                is_verified=True,
                is_active=True,
                tenant_id=None
            )
            db.add(new_super_admin)
            await db.commit()
            print(f"Super_admin {settings.master_admin_username} successfully seeded.", flush=True)

        # Seed default test admin aloksinghrajput2405@gmail.com
        test_email = "aloksinghrajput2405@gmail.com"
        result_test = await db.execute(select(User).where(User.email == test_email))
        test_admin = result_test.scalar_one_or_none()
        if not test_admin:
            print(f"Seeding test administrator {test_email}...", flush=True)
            hashed_pwd = hash_password("Alok@245singh")
            test_admin = User(
                email=test_email,
                hashed_password=hashed_pwd,
                role="admin",
                is_verified=True,
                is_active=True,
                tenant_id=None
            )
            db.add(test_admin)
            await db.commit()
            await db.refresh(test_admin)
            test_admin.tenant_id = test_admin.id
            await db.commit()
            print(f"Test administrator {test_email} successfully seeded.", flush=True)

        # Seed TenantSettings for test admin using system settings env
        from modules.settings.models import TenantSettings
        ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == test_admin.id))
        ts_record = ts_res.scalar_one_or_none()
        if not ts_record:
            print(f"Seeding default TenantSettings for {test_email}...", flush=True)
            ts_record = TenantSettings(
                tenant_id=test_admin.id,
                zoom_account_id=settings.zoom_account_id,
                zoom_client_id=settings.zoom_client_id,
                zoom_client_secret=settings.zoom_client_secret,
                zoom_user_id=settings.zoom_user_id,
                google_calendar_id=settings.google_calendar_id,
                google_sheet_id=settings.google_sheet_id,
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                smtp_username=settings.smtp_username,
                smtp_password=settings.smtp_password,
                smtp_from=settings.smtp_from,
                app_url=settings.app_url,
                timezone_default=settings.timezone_default,
                gemini_api_key=settings.gemini_api_key
            )
            db.add(ts_record)
            await db.commit()
            print(f"Default TenantSettings for {test_email} successfully seeded.", flush=True)
        
    # Populate Agent RAG store
    await initialize_agent_rag()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(classes_router)
app.include_router(courses_router)
app.include_router(zoom_router)
app.include_router(calendar_router)
app.include_router(settings_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(super_admin_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app_name": settings.app_name, "version": settings.app_version}
