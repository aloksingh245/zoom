import os
import httpx
import asyncio
from base64 import b64encode
from dotenv import load_dotenv

async def test_zoom():
    # Load from .env
    load_dotenv()
    
    account_id = os.getenv("ZOOM_ACCOUNT_ID")
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    user_id = os.getenv("ZOOM_USER_ID")

    print("--- Zoom Credentials Test ---")
    print(f"Account ID:     {account_id}")
    print(f"Client ID:      {client_id}")
    print(f"Client Secret:  {client_secret[:4]}...{client_secret[-4:] if client_secret else ''}")
    print(f"User ID:        {user_id}")
    print("-" * 30)

    if not all([account_id, client_id, client_secret]):
        print("ERROR: Missing one or more credentials in .env file.")
        return

    # Use a single client session for all tests
    async with httpx.AsyncClient() as client:
        # 1. Test OAuth Token Generation
        print("\n1. Testing OAuth Token Generation...")
        basic = b64encode(f"{client_id}:{client_secret}".encode()).decode()
        token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
        
        try:
            resp = await client.post(token_url, headers={"Authorization": f"Basic {basic}"})
            if resp.status_code == 200:
                print("SUCCESS: OAuth Token generated successfully.")
                token = resp.json().get("access_token")
            else:
                print(f"FAILED: Status {resp.status_code}")
                print(f"Response Body: {resp.text}")
                return
        except Exception as e:
            print(f"ERROR: Could not connect to Zoom: {e}")
            return

        # 2. Test User/Meeting Scopes
        if user_id:
            print("\n2. Testing Scopes (Listing Meetings)...")
            meetings_url = f"https://api.zoom.us/v2/users/{user_id}/meetings"
            try:
                resp = await client.get(
                    meetings_url, 
                    headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code == 200:
                    print("SUCCESS: Able to list meetings. Your scopes are correct.")
                else:
                    print(f"FAILED: Status {resp.status_code}")
                    print(f"Response Body: {resp.text}")
            except Exception as e:
                print(f"ERROR: Could not fetch meetings: {e}")

if __name__ == "__main__":
    asyncio.run(test_zoom())
