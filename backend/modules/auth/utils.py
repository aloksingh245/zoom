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

def send_verification_email(email: str, token: str):
    verification_link = f"{settings.app_url}/verify-email?token={token}"
    
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning(f"[SMTP MOCK] No SMTP credentials configured. Verification email simulated.")
        print(f"\n==================================================")
        print(f"📧 [SMTP MOCK] Verification email sent to: {email}")
        print(f"🔗 Verification Link: {verification_link}")
        print(f"==================================================\n")
        return
        
    msg = MIMEMultipart()
    msg['From'] = settings.smtp_from
    msg['To'] = email
    msg['Subject'] = "Verify your email - Zoom Scheduler"
    
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
    msg.attach(MIMEText(body, 'html'))
    
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from, email, msg.as_string())
        logger.info(f"Verification email successfully sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
        raise e

def send_reset_password_email(email: str, token: str):
    reset_link = f"{settings.app_url}/reset-password?token={token}"
    
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning(f"[SMTP MOCK] No SMTP credentials configured. Reset password email simulated.")
        print(f"\n==================================================")
        print(f"📧 [SMTP MOCK] Reset password email sent to: {email}")
        print(f"🔗 Reset Password Link: {reset_link}")
        print(f"==================================================\n")
        return
        
    msg = MIMEMultipart()
    msg['From'] = settings.smtp_from
    msg['To'] = email
    msg['Subject'] = "Reset your password - Zoom Scheduler"
    
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
    msg.attach(MIMEText(body, 'html'))
    
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from, email, msg.as_string())
        logger.info(f"Reset password email successfully sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        raise e

