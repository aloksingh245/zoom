import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Standard scopes for Calendar and Events
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]

def main():
    if not os.path.exists("oauth_client.json"):
        print("ERROR: oauth_client.json not found in the backend folder!")
        return

    print("--- Google Calendar Authentication ---")
    print("This script will open your browser to authorize the application.")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        "oauth_client.json", SCOPES
    )
    
    # run_local_server works perfectly with 'Desktop App' credentials
    # It will automatically find an open port and handle the redirect.
    creds = flow.run_local_server(port=0)
    
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    
    print("\n✅ SUCCESS! token.json has been created.")
    print("Google Calendar integration is now ACTIVE.")

if __name__ == "__main__":
    main()
