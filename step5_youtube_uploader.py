import os
import sys
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
# --- REMOVED: moviepy is no longer needed ---
# from moviepy.editor import VideoFileClip
import glob

# --- NEW: Add import for webbrowser ---
import webbrowser
# --- NEW: Add import for running the browser ---
import subprocess
# --- NEW: Import proxy and profile handling libraries ---
from antidetect_browser.browser_profile import BrowserProfile
import httplib2
from google_auth_httplib2 import AuthorizedHttp

# Fix Windows console encoding issues
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows console
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Fallback: Replace problematic Unicode characters
        pass

class YouTubeUploader:
    def __init__(self, config, channel_name, client_secrets_path, credentials_path):
        
        # --- NEW: Store config ---
        self.config = config
        self.channel_name = channel_name
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
        
        # --- NEW: Dynamic credential paths ---
        self.client_secrets_file = client_secrets_path
        self.credentials_file = credentials_path
        self.api_service_name = "youtube"
        self.api_version = "v3"
        # --- NEW: Dynamic credential file per channel ---
        # self.credentials_file = f"token_{channel_name}.pickle" # This line is now redundant

    def get_authenticated_service(self):
        """Authenticates the user and returns the YouTube API service object."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secrets_file):
                    print("ERROR: client_secret.json not found.")
                    print("Please download it from the Google Cloud Console and place it in the project root.")
                    return None
                
                # --- NEW: Launch anti-detect browser for authentication ---
                profile_name = self.config.CHANNEL_TO_PROFILE_MAPPING.get(self.channel_name)
                
                if profile_name:
                    print(f"🚀 Launching anti-detect browser profile '{profile_name}' for authentication...")
                    try:
                        # Assumes the browser app is in the antidetect_browser directory
                        browser_app_path = os.path.join('antidetect_browser', 'main_app.py')
                        subprocess.Popen([sys.executable, browser_app_path, '--profile', profile_name])
                        print("Please complete the authentication in the browser that just opened.")
                    except Exception as e:
                        print(f"⚠️  WARNING: Could not automatically launch the anti-detect browser: {e}")
                        print("Please open it manually to the correct profile and continue.")

                # --- FIX: Programmatically remove restrictive redirect_uris ---
                # Load the client secrets file manually
                with open(self.client_secrets_file, 'r') as f:
                    client_config = json.load(f)

                # This key, when present, prevents the library from using a dynamic port for its local server.
                if 'installed' in client_config and 'redirect_uris' in client_config['installed']:
                    print("DEBUG: Found and removed restrictive 'redirect_uris' key from credentials.")
                    del client_config['installed']['redirect_uris']

                # Create the flow from the modified configuration instead of the file
                flow = InstalledAppFlow.from_client_config(client_config, self.scopes)
                
                print("\n--- ACTION REQUIRED ---")
                print("1. Your anti-detect browser has launched.")
                print("2. Copy the URL below and paste it into the anti-detect browser's address bar.")
                
                # Get the authorization URL and print it once
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"\n🔗 COPY THIS URL: {auth_url}")
                print("👆 Copy the URL above and paste it into your browser")
                
                creds = flow.run_local_server(port=0, open_browser=False)
            
            # Save the credentials for the next run
            with open(self.credentials_file, 'wb') as token:
                pickle.dump(creds, token)

        try:
            # --- FIX: Correctly apply proxy to the HTTP client ---
            http = httplib2.Http() # Start with a default client
            profile_name = self.config.CHANNEL_TO_PROFILE_MAPPING.get(self.channel_name)
            
            if profile_name:
                profile = BrowserProfile.load_profile(profile_name)
                if profile and profile.proxy_config:
                    proxy_cfg = profile.proxy_config
                    if proxy_cfg.get('host') and proxy_cfg.get('port'):
                        print(f"INFO: Configuring API calls to use proxy: {proxy_cfg['host']}:{proxy_cfg['port']}")
                        proxy_info = httplib2.ProxyInfo(
                            proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                            proxy_host=proxy_cfg['host'],
                            proxy_port=proxy_cfg['port'],
                            proxy_user=proxy_cfg.get('username'),
                            proxy_pass=proxy_cfg.get('password')
                        )
                        # Create a new Http object with the proxy info
                        http = httplib2.Http(proxy_info=proxy_info)

            # Wrap the http client with the credentials to authorize it
            authed_http = AuthorizedHttp(creds, http=http)

            service = build(self.api_service_name, self.api_version, http=authed_http)
            return service
            
        except HttpError as e:
            print(f"An error occurred while building the service: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during service creation: {e}")
            return None

    def _get_current_channel_name(self, youtube):
        """Fetches and returns the name of the authenticated YouTube channel."""
        try:
            response = youtube.channels().list(
                part="snippet",
                mine=True
            ).execute()
            
            if response["items"]:
                channel_title = response["items"][0]["snippet"]["title"]
                return channel_title
            else:
                return "Unknown Channel"
        except HttpError as e:
            print(f"  WARNING: Could not fetch channel name. Error: {e}")
            return "Unknown Channel"

    def _generate_timestamps_from_data(self, data, intro_duration=5):
        """Generates a YouTube chapters string from pre-calculated durations."""
        print("Generating timestamps from saved data...")
        
        intro_text = getattr(self.config, 'YOUTUBE_INTRO_CHAPTER', "Intro")
        timestamps = [
            "\n\nTIMESTAMPS:",
            f"00:00 - {intro_text}"
        ]
        cumulative_duration = intro_duration  # Start after the intro

        products = sorted(data.get('products', []), key=lambda p: p.get('position', 99))

        for product in products:
            minutes, seconds = divmod(int(cumulative_duration), 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"
            
            title = product.get('short_title', 'Product')
            position = product.get('position')
            timestamps.append(f"{timestamp_str} - N°{position}: {title}")

            # --- NEW: Read duration directly from data ---
            segment_duration = product.get('segment_duration')
            if segment_duration:
                cumulative_duration += segment_duration
            else:
                print(f"  WARNING: 'segment_duration' not found for product {position}. Using default of 30s.")
                cumulative_duration += 30 # Default fallback

        return "\n".join(timestamps)

    def find_latest_video(self):
        """Finds the most recently created video file in the output directory."""
        video_dir = self.config.OUTPUT_DIR # Corrected from VIDEOS_DIR to OUTPUT_DIR
        if not os.path.exists(video_dir):
            return None
        
        files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith('.mp4')]
        if not files:
            return None
            
        latest_file = max(files, key=os.path.getctime)
        return latest_file

    def find_latest_thumbnail(self, keyword):
        """Finds the most recently created thumbnail file for a given keyword."""
        thumb_dir = self.config.OUTPUT_DIR
        if not os.path.exists(thumb_dir):
            return None
        
        # Search for thumbnails matching the keyword pattern
        safe_keyword = keyword.replace(' ', '_')
        pattern = os.path.join(thumb_dir, f"thumbnail_{safe_keyword}.png")
        files = [f for f in glob.glob(pattern)]
        
        if not files:
            print(f"  WARNING: No thumbnail found for keyword '{keyword}'.")
            return None
            
        latest_file = max(files, key=os.path.getctime)
        return latest_file

    def _upload_thumbnail(self, youtube, video_id, keyword):
        """Uploads a custom thumbnail to a video."""
        thumbnail_path = self.find_latest_thumbnail(keyword)
        if not thumbnail_path:
            return

        print(f"Uploading custom thumbnail: {os.path.basename(thumbnail_path)}")
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("SUCCESS: Custom thumbnail was successfully uploaded.")
        except HttpError as e:
            print(f"ERROR: An error occurred while uploading the thumbnail: {e}")

    def upload_video(self, publish_at=None):
        """Main function to upload the video to YouTube."""
        print("STEP 5: Uploading Video to YouTube")
        print("=" * 50)
        
        youtube = self.get_authenticated_service()
        if not youtube:
            print("ERROR: Could not authenticate with YouTube. Aborting upload.")
            return

        # --- NEW: Verify Channel Name ---
        channel_name = self._get_current_channel_name(youtube)
        print(f"SUCCESS: Authenticated as YouTube Channel: '{channel_name}'")
        # --- END ---

        # 1. Find the video file
        video_path = self.find_latest_video()
        if not video_path:
            print("ERROR: No video file found to upload in the 'output' directory.")
            return
        print(f"SUCCESS: Found video to upload: {os.path.basename(video_path)}")

        # 2. Load metadata from enhanced_product.json
        data_file = os.path.join(self.config.OUTPUT_DIR, "enhanced_product.json")
        if not os.path.exists(data_file):
            print(f"ERROR: Enhanced data file not found at '{data_file}'.")
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keyword = data.get('keyword', 'Top Products')
        product_count = len(data.get('products', []))
        products = sorted(data.get('products', []), key=lambda p: p.get('position', 99))


        # 3. Define video details from config
        title_template = getattr(self.config, 'YOUTUBE_TITLE', "Top {product_count} Best {keyword} in 2025")
        title = title_template.format(product_count=product_count, keyword=keyword.title())
        
        # --- Build Description with Affiliate Links ---
        description_parts = []
        lead_in_template = getattr(self.config, 'YOUTUBE_DESCRIPTION_LEAD_IN', "👇 Find the best {keyword} tested in this video 👇")
        description_parts.append(lead_in_template.format(keyword=keyword) + "\n")

        for product in products:
            position = product.get('position')
            product_title = product.get('title', '').strip()
            price = product.get('price', '')
            asin = product.get('asin')
            
            # Construct affiliate link from config
            amazon_tld = getattr(self.config, 'AMAZON_TLD', 'fr')
            affiliate_tag = getattr(self.config, 'AMAZON_TAG', '')

            if asin and affiliate_tag:
                link = f"https://www.amazon.{amazon_tld}/dp/{asin}/?tag={affiliate_tag}"
            else:
                link = product.get('url', '')

            product_line_template = getattr(self.config, 'YOUTUBE_PRODUCT_LINE', "N°{position}: ({price}) 👉 {link}")
            description_parts.append(product_line_template.format(
                position=position,
                price=price,
                link=link
            ))

        disclaimer = getattr(self.config, 'YOUTUBE_DISCLAIMER', "Disclaimer: ...")
        description_parts.append(f"\n\n{disclaimer}")
        
        description = "\n".join(description_parts)
        # --- End Description Build ---
        
        tags = [keyword, f"best {keyword}", f"top {keyword}", "review", "test"]

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # 22 = People & Blogs
            },
            "status": {
                "privacyStatus": "public", # 'public', 'private', or 'unlisted'
                "selfDeclaredMadeForKids": False
            }
        }
        
        # --- NEW: Handle Scheduled Uploads ---
        if publish_at:
            request_body["status"]["privacyStatus"] = "private"
            request_body["status"]["publishAt"] = publish_at
            print(f"SCHEDULED: Video will be private until scheduled publish time: {publish_at}")
        # --- END ---

        # 4. Perform the upload
        print("Uploading video to YouTube...")
        try:
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            request = youtube.videos().insert(
                part=",".join(request_body.keys()),
                body=request_body,
                media_body=media
            )
            
            response = request.execute()
            
            video_id = response.get("id")
            print("\n" + "="*50)
            print("VIDEO UPLOAD COMPLETE!")
            print(f"SUCCESS: Video '{title}' was successfully uploaded.")
            if video_id:
                print(f"Watch on YouTube: https://www.youtube.com/watch?v={video_id}")
                
                # --- UPDATED: Use new function to add timestamps ---
                print("\nAdding timestamps to video description...")
                timestamp_block = self._generate_timestamps_from_data(data)
                updated_description = description + timestamp_block
                
                update_body = {
                    "id": video_id,
                    "snippet": {
                        "title": title,
                        "description": updated_description,
                        "tags": tags,
                        "categoryId": "22"
                    }
                }
                
                try:
                    youtube.videos().update(
                        part="snippet",
                        body=update_body
                    ).execute()
                    print("SUCCESS: Timestamps successfully added!")
                except HttpError as e:
                    print(f"ERROR: Failed to update video with timestamps. Error: {e}")
                
                # --- NEW: Upload Thumbnail ---
                self._upload_thumbnail(youtube, video_id, keyword)
                
                # Comment posting is now handled by post_missing_comments.py
                # after the video is public.

        except HttpError as e:
            print(f"\nERROR: An HTTP error {e.resp.status} occurred:\n{e.content}")

if __name__ == "__main__":
    import sys
    import argparse
    from config import get_config

    parser = argparse.ArgumentParser(description="Standalone YouTube uploader for a specific language.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    parser.add_argument('--channel', type=str, required=True, help="A unique name for the YouTube channel credential file (e.g., 'MyTechChannel').")
    parser.add_argument('--publish-at', type=str, help="ISO 8601 format date/time to schedule the video for (e.g., '2024-12-31T10:00:00Z').")
    # --- NEW: Arguments for credential paths (for standalone use) ---
    parser.add_argument('--secrets-path', type=str, default='credentials/client1.json', help="Path to the client_secret.json file.")
    parser.add_argument('--token-path', type=str, help="Path to the token .pickle file. If not provided, it's generated from channel name.")
    # --- NEW: Add arguments for session directories ---
    parser.add_argument('--output-dir', type=str, help="Override default output directory.")
    parser.add_argument('--audio-dir', type=str, help="Override default audio directory.")
    parser.add_argument('--videos-dir', type=str, help="Override default videos directory.")
    args = parser.parse_args()

    try:
        print(f"Running Step 5 in standalone mode for language '{args.language}'")
        Config = get_config(args.language)
        print(f"Loaded configuration for language: {Config.CONTENT_LANGUAGE}")

        # --- NEW: Override config paths if provided ---
        if args.output_dir:
            Config.OUTPUT_DIR = args.output_dir
            print(f"   Overriding OUTPUT_DIR: {Config.OUTPUT_DIR}")
        # audio-dir and videos-dir are not used in this script, but we accept them for consistency

        # --- MODIFIED: Handle token path generation in the 'tokens' directory ---
        token_path = args.token_path
        if not token_path:
            # Use channel name directly for token path
            token_path = os.path.join('tokens', f"token_{args.channel}.pickle")

        # Pass the credential paths to the uploader
        uploader = YouTubeUploader(Config, args.channel, args.secrets_path, token_path)
        uploader.upload_video(publish_at=args.publish_at)

    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1) 