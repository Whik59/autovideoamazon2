import os
import pickle
import glob
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import sys
import subprocess
from config import get_config
import json

def authorize_credentials():
    """
    Checks for client_<channel_name>.json files in the 'credentials' directory
    and runs the OAuth 2.0 flow for any that don't have a corresponding
    token. This process now uses an anti-detect browser profile for login.
    """
    print("🔑 Starting credential authorization process...")
    
    # Define the scopes and directories
    credentials_dir = "credentials"
    token_dir = "tokens"
    scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
    os.makedirs(token_dir, exist_ok=True)

    # --- NEW: Load base config to get profile mapping ---
    # We load 'en' as a default, but the mapping should be in base.py
    try:
        Config = get_config('en') 
        profile_mapping = Config.CHANNEL_TO_PROFILE_MAPPING
        if not profile_mapping:
            print("⚠️  WARNING: The CHANNEL_TO_PROFILE_MAPPING in 'config/base.py' is empty.")
            print("   The script will use the default browser for authentication.")
    except (ImportError, AttributeError):
        print("⚠️  WARNING: Could not load CHANNEL_TO_PROFILE_MAPPING from config.")
        print("   The script will use the default browser for authentication.")
        profile_mapping = {}

    # Find all client secret files matching the new format
    secret_files = glob.glob(os.path.join(credentials_dir, '*.json'))
    
    if not secret_files:
        print("❌ No '.json' files found in the 'credentials' directory.")
        print("   Please create your Google Cloud projects and place the downloaded JSON files there,")
        print("   named according to the channel they are for (e.g., 'MyChannel.json').")
        return

    print(f"Found {len(secret_files)} client secret files. Checking for existing tokens...")

    authorized_count = 0
    for secret_file in sorted(secret_files):
        # Derive channel name and token path from the secret file name
        base_name = os.path.basename(secret_file)
        
        # Extract channel name from filename (e.g., 'top3cuisine.json' -> 'top3cuisine')
        channel_name = base_name.replace('.json', '')
        
        # Skip if it's an old token file that got mixed in
        if channel_name.startswith('token_'):
            continue

        token_file = os.path.join(token_dir, f"token_{channel_name}.pickle")
        
        creds = None
        if os.path.exists(token_file):
            print(f"✅ Token already exists for channel '{channel_name}'. Skipping.")
            authorized_count += 1
            continue
            
        print(f"\n--- Authorizing Channel: {channel_name} ---")
        
        # If there are no (valid) credentials available, let the user log in.
        try:
            # --- NEW: Launch anti-detect browser for authentication ---
            profile_name = profile_mapping.get(channel_name)
            
            if profile_name:
                print(f"🚀 Launching anti-detect browser profile '{profile_name}' for authentication...")
                try:
                    browser_app_path = os.path.join('antidetect_browser', 'main_app.py')
                    subprocess.Popen([sys.executable, browser_app_path, '--profile', profile_name])
                    print("Please complete the authentication in the browser that just opened.")
                except Exception as e:
                    print(f"⚠️  WARNING: Could not automatically launch the anti-detect browser: {e}")
                    print("Please open it manually to the correct profile and continue.")
            
            # --- FIX: Programmatically remove restrictive redirect_uris ---
            with open(secret_file, 'r') as f:
                client_config = json.load(f)

            if 'installed' in client_config and 'redirect_uris' in client_config['installed']:
                print("DEBUG: Found and removed restrictive 'redirect_uris' key from credentials.")
                del client_config['installed']['redirect_uris']

            flow = InstalledAppFlow.from_client_config(client_config, scopes)
            
            # Use local server instead of console for OAuth flow
            print("\n--- ACTION REQUIRED ---")
            print("1. Your anti-detect browser has launched (or will launch).")
            print("2. Copy the URL below and paste it into the anti-detect browser's address bar.")

            # Get the authorization URL and print it once
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"\n🔗 COPY THIS URL: {auth_url}")
            print("👆 Copy the URL above and paste it into your browser")

            creds = flow.run_local_server(port=0, open_browser=False)
            
            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            print(f"✅ Successfully authorized '{channel_name}' and saved token to '{token_file}'")
            authorized_count += 1
        except Exception as e:
            print(f"❌ Failed to authorize {channel_name}.")
            print(f"   Error: {e}")
            print("   Please try again.")
            
    print("\n" + "="*50)
    if authorized_count == len(secret_files):
        print("🎉 All credentials have been authorized successfully!")
    else:
        print(f"⚠️  {authorized_count}/{len(secret_files)} credentials have been authorized.")
        print("   Run the script again to complete the remaining authorizations.")
    print("="*50)

if __name__ == '__main__':
    authorize_credentials() 