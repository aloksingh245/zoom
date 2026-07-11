"""
output_guard.py — Sanitizes the generated text before it streams to the user.

WHY SANITIZE OUTPUT?
  1. Data Leakage: Ensure students do not receive host links (zoom_start_url).
  2. Credentials Protection: Prevent the model from outputting environment variables, database keys, or passwords.
  3. LLM Hallucinations: If the model prints standard debug code containing API paths/keys.
"""

import re
import logging

logger = logging.getLogger(__name__)

from core.config import settings

# Patterns to match API keys, passwords, and tokens
SECRET_PATTERNS = [
    r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",  # JWT token pattern
    r"AIzaSy[A-Za-z0-9-_]{33}",  # Google API key pattern
    r"bearer\s+[a-zA-Z0-9_\-\.]+",  # Bearer token pattern
]

# Patterns representing zoom start URLs (host link)
ZOOM_START_URL_PATTERN = r"https?://[a-zA-Z0-9_\-\.]*zoom\.us/s/[a-zA-Z0-9_\-\.\?&=]+"

def scrub_secrets(text: str) -> str:
    """Scrub JWT tokens, bearer tokens, or Google API keys from text."""
    scrubbed = text
    # 1. Scrub matches from regex patterns
    for pattern in SECRET_PATTERNS:
        scrubbed = re.sub(pattern, "[SECRET REDACTED]", scrubbed, flags=re.IGNORECASE)
    
    # 2. Dynamic environment variable scrubbing (Zero-Trust secret protection)
    sensitive_values = [
        settings.zoom_client_secret,
        settings.smtp_password,
        settings.gemini_api_key,
        settings.jwt_secret,
        settings.zoom_bearer_token,
    ]
    for val in sensitive_values:
        if val and len(str(val)) > 4:
            scrubbed = scrubbed.replace(str(val), "[SECRET REDACTED]")
            
    return scrubbed

def sanitize_zoom_links(text: str, user_role: str) -> str:
    """
    Ensure students NEVER receive the Zoom 'start_url' (host/mentor url).
    If one is found and the user is a student, replace it with a redacted label.
    """
    if user_role == "student":
        match = re.search(ZOOM_START_URL_PATTERN, text)
        if match:
            logger.warning("Intercepted Zoom host link (start_url) in student output stream. Redacting.")
            # Redact the start url entirely
            text = re.sub(ZOOM_START_URL_PATTERN, "[HOST LINK HIDDEN - Ask Admin/Mentor]", text)
    return text

def run_output_guardrails(text: str, user_role: str) -> str:
    """
    Run output sanitizations on a text block.
    Returns the sanitized string.
    """
    text = scrub_secrets(text)
    text = sanitize_zoom_links(text, user_role)
    return text
