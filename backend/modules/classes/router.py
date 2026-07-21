from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.classes import schemas
from modules.classes.service import class_service
from modules.auth.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/api/classes", tags=["classes"])

# In-memory PKCE store: maps OAuth state -> code_verifier
# Needed because /auth and /callback are separate requests with separate Flow instances
_pkce_store: dict = {}

@router.get("", response_model=List[schemas.ClassSession])
async def list_classes(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    return await class_service.list_classes(db, tenant_id)

@router.get("/{class_id}", response_model=schemas.ClassSession)
async def get_class(class_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    return await class_service.get_class(db, class_id, tenant_id)

@router.post("", response_model=schemas.ClassSession)
async def create_class(payload: schemas.ClassCreate, db: AsyncSession = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    return await class_service.create_class(db, payload, current_user.tenant_id)

@router.put("/{class_id}", response_model=schemas.ClassSession)
async def update_class(class_id: str, payload: schemas.ClassUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    return await class_service.update_class(db, class_id, payload, current_user.tenant_id)

@router.post("/sync")
async def sync_classes(db: AsyncSession = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    return await class_service.sync_with_zoom(db, current_user.tenant_id)

@router.post("/sync/calendar")
async def sync_with_calendar(db: AsyncSession = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    return await class_service.sync_with_calendar(db, current_user.tenant_id)

@router.get("/sync/calendar/status")
async def get_calendar_status(current_user = Depends(get_current_user)):
    """Check if Google Calendar is authenticated."""
    from integrations.google_calendar.client import calendar_service
    import asyncio
    creds = await asyncio.to_thread(calendar_service._get_credentials)
    return {"connected": creds is not None}

@router.get("/sync/calendar/auth")
async def calendar_auth(current_user = Depends(RoleChecker(["admin"]))):
    """Generate Google Calendar authorization URL with explicit PKCE."""
    from google_auth_oauthlib.flow import Flow
    import os
    import secrets
    import hashlib
    import base64
    from fastapi import HTTPException
    from core.config import settings
    import logging

    logger = logging.getLogger(__name__)

    if not os.path.exists("oauth_client.json"):
        raise HTTPException(
            status_code=400,
            detail="Google Client Secrets (oauth_client.json) not found on backend."
        )

    # Allow HTTP for local development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ]

    redirect_uri = f"{settings.backend_url}/api/classes/sync/calendar/callback"

    flow = Flow.from_client_secrets_file(
        "oauth_client.json",
        scopes=scopes,
        redirect_uri=redirect_uri
    )

    # Explicitly generate PKCE — Google requires this for web clients
    code_verifier = secrets.token_urlsafe(96)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    # Store verifier keyed by OAuth state for retrieval in callback
    _pkce_store[state] = code_verifier
    logger.info(f"PKCE generated and stored — state: {state[:8]}..., verifier_len: {len(code_verifier)}")

    return {"auth_url": auth_url}

@router.get("/sync/calendar/callback")
async def calendar_callback(code: str, state: str = None):
    """Google OAuth callback. Exchanges authorization code for credentials."""
    from google_auth_oauthlib.flow import Flow
    from fastapi.responses import HTMLResponse
    from fastapi import HTTPException
    from core.config import settings
    import os
    import logging
    import traceback

    logger = logging.getLogger(__name__)

    # Allow HTTP for local development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    if not os.path.exists("oauth_client.json"):
        raise HTTPException(status_code=400, detail="oauth_client.json not found.")

    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ]

    redirect_uri = f"{settings.backend_url}/api/classes/sync/calendar/callback"
    logger.info(f"OAuth callback — redirect_uri: {redirect_uri}")

    flow = Flow.from_client_secrets_file(
        "oauth_client.json",
        scopes=scopes,
        redirect_uri=redirect_uri
    )

    try:
        # Retrieve PKCE code_verifier stored during /auth step
        code_verifier = _pkce_store.pop(state, None)
        if code_verifier:
            logger.info(f"PKCE code_verifier found for state: {state[:8] if state else 'None'}...")
        else:
            logger.warning("No PKCE code_verifier found — proceeding without it.")

        flow.fetch_token(code=code, code_verifier=code_verifier)
        creds = flow.credentials
        
        # Manually attach client details from the flow configuration so they are serialized
        creds.client_id = flow.client_config.get("client_id")
        creds.client_secret = flow.client_config.get("client_secret")

        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

        logger.info("Google Calendar token saved successfully with client details.")
        frontend_url = settings.app_url or "http://localhost:5173"

        html_content = f"""
        <html>
            <head>
                <title>Authentication Successful</title>
                <style>
                    body {{
                        font-family: system-ui, -apple-system, sans-serif;
                        background-color: #f8fafc;
                        color: #0f172a;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .card {{
                        background: white;
                        padding: 2.5rem;
                        border-radius: 2rem;
                        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
                        text-align: center;
                        max-width: 400px;
                        border: 1px solid #e2e8f0;
                    }}
                    h1 {{ color: #4f46e5; margin-bottom: 1rem; }}
                    p {{ color: #64748b; font-size: 0.95rem; margin-bottom: 2rem; }}
                    .btn {{
                        background-color: #4f46e5;
                        color: white;
                        padding: 0.75rem 1.5rem;
                        border-radius: 1rem;
                        text-decoration: none;
                        font-weight: bold;
                        font-size: 0.9rem;
                        transition: background 0.2s;
                    }}
                    .btn:hover {{ background-color: #4338ca; }}
                </style>
                <script>
                    setTimeout(function() {{
                        window.location.href = "{frontend_url}?gcal_success=true";
                    }}, 2000);
                </script>
            </head>
            <body>
                <div class="card">
                    <h1>Calendar Connected!</h1>
                    <p>Google Calendar has been successfully authenticated. Redirecting you back to the dashboard...</p>
                    <a class="btn" href="{frontend_url}?gcal_success=true">Return to Dashboard</a>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Google Authentication failed: {str(e)}")

@router.delete("/{class_id}")
async def delete_class(class_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    await class_service.delete_class(db, class_id, current_user.tenant_id)
    return {"deleted": True}
