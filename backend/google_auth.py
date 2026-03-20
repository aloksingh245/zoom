import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]

def main():
    if not os.path.exists("oauth_client.json"):
        print("ERROR: oauth_client.json not found!")
        print("Please download your OAuth 2.0 Client ID JSON from Google Cloud Console")
        print("and save it as 'oauth_client.json' in the backend folder.")
        return

    print("Starting authentication flow...")
    flow = InstalledAppFlow.from_client_secrets_file(
        "oauth_client.json", SCOPES
    )
    
    # This will open a browser window for you to log in
    creds = flow.run_local_server(port=0)
    
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    
    print("\n✅ SUCCESS! token.json has been created.")
    print("Your application can now send Calendar Invites directly from your email.")

if __name__ == "__main__":
    main()
