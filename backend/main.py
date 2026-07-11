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

# Import models to ensure they are registered with Base metadata
from modules.auth import models as auth_models

# Import Event Listeners to register them
from integrations.google_calendar.listeners import register_listeners as register_calendar_listeners
from integrations.google_sheets.listeners import register_listeners as register_sheets_listeners
from integrations.crm.listeners import register_listeners as register_crm_listeners
from modules.agent.listeners import register_listeners as register_agent_listeners

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
    register_calendar_listeners()
    register_sheets_listeners()
    register_crm_listeners()
    register_agent_listeners()
    
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
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


@app.get("/health")
async def health():
    return {"status": "ok", "app_name": settings.app_name, "version": settings.app_version}
