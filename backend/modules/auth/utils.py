from datetime import datetime, timedelta
import jwt
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from core.config import settings

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    try:
        decoded = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return decoded
    except jwt.PyJWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        return None

import urllib.request
import json

def _send_brevo_email(to_email: str, subject: str, body: str, fallback_message: str, link: str):
    is_mock = not settings.brevo_api_key
    if is_mock:
        logger.warning(f"[EMAIL MOCK] No API key configured. Email simulated.")
        print(f"\n==================================================")
        print(f"📧 [EMAIL MOCK] Email sent to: {to_email}")
        print(f"🔗 Link: {link}")
        print(f"==================================================\n")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": "Zoom Scheduler", "email": settings.email_user or settings.smtp_from},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": body
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response.read()
            logger.info(f"Email successfully sent via Brevo API to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email} due to API error: {e}")
        print(f"\n==================================================")
        print(f"📧 {fallback_message} Recovery link for {to_email}:")
        print(f"🔗 Link: {link}")
        print(f"==================================================\n", flush=True)

def send_verification_email(email: str, token: str):
    verification_link = f"{settings.app_url}/verify-email?token={token}"
    body = f"""
    <html>
        <body>
            <h2 style="color: #4f46e5;">Welcome to Zoom Scheduler!</h2>
            <p>Thank you for signing up. Please click the link below to verify your email and activate your account:</p>
            <p>
                <a href="{verification_link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                    Verify Email Address
                </a>
            </p>
            <p>If you did not request this, please ignore this email.</p>
            <br>
            <p style="color: #64748b; font-size: 12px;">Zoom Scheduler Team</p>
        </body>
    </html>
    """
    _send_brevo_email(email, "Verify your email - Zoom Scheduler", body, "[API FALLBACK] Verification email failed.", verification_link)

def send_reset_password_email(email: str, token: str):
    reset_link = f"{settings.app_url}/reset-password?token={token}"
    body = f"""
    <html>
        <body>
            <h2 style="color: #4f46e5;">Reset Your Password</h2>
            <p>We received a request to reset the password for your Zoom Scheduler account. Click the button below to set a new password:</p>
            <p>
                <a href="{reset_link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>This reset link will expire in 15 minutes. If you did not request a password reset, please ignore this email.</p>
            <br>
            <p style="color: #64748b; font-size: 12px;">Zoom Scheduler Team</p>
        </body>
    </html>
    """
    _send_brevo_email(email, "Reset your password - Zoom Scheduler", body, "[API FALLBACK] Reset email failed.", reset_link)

