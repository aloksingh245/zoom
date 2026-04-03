from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import engine, Base

# Import Routers
from modules.classes.router import router as classes_router
from modules.courses.router import router as courses_router
from modules.ai.router import router as ai_router
from integrations.zoom.router import router as zoom_router
from integrations.google_calendar.router import router as calendar_router

# Import Event Listeners to register them
from integrations.google_calendar.listeners import register_listeners as register_calendar_listeners
from integrations.google_sheets.listeners import register_listeners as register_sheets_listeners

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
    
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(classes_router)
app.include_router(courses_router)
app.include_router(ai_router)
app.include_router(zoom_router)
app.include_router(calendar_router)

@app.get("/health")
async def health():
    return {"status": "ok", "app_name": settings.app_name, "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
