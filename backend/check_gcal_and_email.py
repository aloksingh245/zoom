import os
import smtplib
import dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

dotenv.load_dotenv()

def check_email():
    print("--- Checking Brevo SMTP Email Configuration ---")
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 587))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM")

    print(f"SMTP Host: {host}")
    print(f"SMTP Port: {port}")
    print(f"SMTP Username: {username}")
    print(f"SMTP Sender: {sender}")

    if "YOUR_BREVO" in username or "YOUR_BREVO" in password:
        print("❌ Error: SMTP Username or Password contains placeholder strings.")
        return False

    try:
        print("Connecting to Brevo SMTP Server...")
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            print("Logging in to Brevo SMTP Server...")
            server.login(username, password)
            print("✅ Success: Brevo SMTP credentials authorized successfully.")
            return True
    except Exception as e:
        print(f"❌ Error connecting to SMTP server: {e}")
        return False

def check_calendar():
    print("\n--- Checking Google Calendar Configuration ---")
    token_path = "token.json"
    if not os.path.exists(token_path):
        print("❌ Error: token.json not found. Please connect your Google Calendar in the browser dashboard.")
        return False
    
    try:
        print("Loading credentials from token.json...")
        creds = Credentials.from_authorized_user_file(token_path)
        print("Building Google Calendar Service...")
        service = build('calendar', 'v3', credentials=creds)
        print("Fetching primary calendar information...")
        calendar = service.calendars().get(calendarId='primary').execute()
        print(f"✅ Success: Connected to Google Calendar '{calendar.get('summary')}' ({calendar.get('id')})")
        return True
    except Exception as e:
        print(f"❌ Error connecting to Google Calendar: {e}")
        return False

if __name__ == "__main__":
    email_ok = check_email()
    calendar_ok = check_calendar()
    print("\n--- Summary ---")
    print(f"Email Status: {'PASS' if email_ok else 'FAIL'}")
    print(f"Calendar Status: {'PASS' if calendar_ok else 'FAIL'}")
