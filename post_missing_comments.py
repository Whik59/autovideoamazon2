import os
import sys
import json
import pickle
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import get_config
import subprocess # Add subprocess for browser launch

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

class YouTubeCommentManager:
    def __init__(self, config, channel_name, client_secrets_path, credentials_path):
        self.config = config
        self.channel_name = channel_name # Store channel name
        self.client_secrets_file = client_secrets_path
        self.credentials_file = credentials_path
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    def get_authenticated_service(self):
        """Authenticates the user and returns the YouTube API service object."""
        creds = None
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'rb') as token:
                creds = pickle.load(token)

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
                        browser_app_path = os.path.join('antidetect_browser', 'main_app.py')
                        subprocess.Popen([sys.executable, browser_app_path, '--profile', profile_name])
                    except Exception as e:
                        print(f"⚠️  WARNING: Could not automatically launch the anti-detect browser: {e}")

                # --- FIX: Programmatically remove restrictive redirect_uris ---
                with open(self.client_secrets_file, 'r') as f:
                    client_config = json.load(f)

                if 'installed' in client_config and 'redirect_uris' in client_config['installed']:
                    print("DEBUG: Found and removed restrictive 'redirect_uris' key from credentials.")
                    del client_config['installed']['redirect_uris']

                flow = InstalledAppFlow.from_client_config(client_config, self.scopes)
                
                print("\n--- ACTION REQUIRED ---")
                print("1. Your anti-detect browser has launched.")
                print("2. A localhost URL will be printed below.")
                print("3. Manually COPY the localhost URL and PASTE it into the anti-detect browser.")
                
                creds = flow.run_local_server(port=0, open_browser=False)
            
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

    def get_channel_videos(self, youtube, max_results=50):
        """Get recent videos from the authenticated channel."""
        try:
            # Get the channel's uploads playlist
            channels_response = youtube.channels().list(
                part="contentDetails",
                mine=True
            ).execute()

            if not channels_response["items"]:
                print("ERROR: No channel found for authenticated account.")
                return []

            uploads_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Get videos from the uploads playlist
            playlist_items_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()

            videos = []
            for item in playlist_items_response["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                title = item["snippet"]["title"]
                published_at = item["snippet"]["publishedAt"]
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "published_at": published_at
                })

            return videos

        except HttpError as e:
            print(f"ERROR: Could not fetch channel videos: {e}")
            return []

    def get_video_details(self, youtube, video_id):
        """Get video details including description and privacy status."""
        try:
            response = youtube.videos().list(
                part="snippet,status",
                id=video_id
            ).execute()

            if not response["items"]:
                return None

            video = response["items"][0]
            return {
                "description": video["snippet"]["description"],
                "privacy_status": video["status"]["privacyStatus"],
                "title": video["snippet"]["title"]
            }

        except HttpError as e:
            print(f"ERROR: Could not fetch video details for {video_id}: {e}")
            return None

    def has_pinned_comment_from_channel(self, youtube, video_id):
        """Check if the video already has a pinned comment from the channel owner."""
        try:
            # Get comments for the video
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                order="relevance",
                maxResults=10
            ).execute()

            channel_response = youtube.channels().list(
                part="id",
                mine=True
            ).execute()

            if not channel_response["items"]:
                return False

            channel_id = channel_response["items"][0]["id"]

            # Check if any of the top comments are from the channel owner and pinned
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]
                author_channel_id = comment.get("authorChannelId", {}).get("value", "")
                
                # Check if this comment is from the channel owner
                if author_channel_id == channel_id:
                    # Check if it contains affiliate links (indicating it's our affiliate comment)
                    if "amazon." in comment["textOriginal"].lower() or "👉" in comment["textOriginal"]:
                        print(f"  Found existing affiliate comment from channel owner.")
                        return True

            return False

        except HttpError as e:
            print(f"  WARNING: Could not check comments for video {video_id}: {e}")
            return True  # Assume it has comments to avoid duplicate attempts

    def extract_affiliate_links_from_description(self, description):
        """Extract affiliate links from video description."""
        lines = description.split('\n')
        affiliate_lines = []
        
        for line in lines:
            # Look for lines with product numbers and Amazon links
            if re.search(r'N°\d+.*amazon\.[a-z]+', line, re.IGNORECASE):
                affiliate_lines.append(line.strip())
            elif re.search(r'👉.*amazon\.[a-z]+', line, re.IGNORECASE):
                affiliate_lines.append(line.strip())
        
        return affiliate_lines

    def post_affiliate_comment(self, youtube, video_id, video_title, affiliate_links):
        """Post and pin an affiliate comment on the video."""
        if not affiliate_links:
            print(f"  WARNING: No affiliate links found in description for '{video_title}'")
            return

        # Build comment text using language-specific configuration
        comment_intro_template = getattr(self.config, 'YOUTUBE_PINNED_COMMENT', "👇 Find the best products tested in this video 👇\n\n")
        # Extract keyword from video title if possible (for dynamic text)
        keyword = "products"  # Default fallback
        # Try to extract keyword from title (assumes format like "top 3 Best KEYWORD 2025")
        import re
        keyword_match = re.search(r'Best\s+(\w+)\s+(?:in\s+)?202[0-9]', video_title, re.IGNORECASE)
        if keyword_match:
            keyword = keyword_match.group(1).lower()
        
        comment_intro = comment_intro_template.format(keyword=keyword)
        comment_text = comment_intro + "\n".join(affiliate_links)

        try:
            # Post the comment
            comment_body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
            
            comment_response = youtube.commentThreads().insert(
                part="snippet",
                body=comment_body
            ).execute()
            
            comment_id = comment_response["snippet"]["topLevelComment"]["id"]
            print(f"  SUCCESS: Posted affiliate comment (ID: {comment_id})")

            # Try to pin the comment (this might not work for all videos)
            try:
                youtube.comments().setModerationStatus(
                    id=comment_id,
                    moderationStatus="published",
                    banAuthor=False
                ).execute()
                print(f"  SUCCESS: Comment {comment_id} has been pinned.")
            except HttpError as pin_error:
                print(f"  WARNING: Could not pin comment (but comment was posted): {pin_error}")

        except HttpError as e:
            print(f"  ERROR: Could not post comment: {e}")

    def process_videos_missing_comments(self, max_videos=20):
        """Main function to find and add missing affiliate comments."""
        print("COMMENT MANAGER: Finding videos without affiliate comments")
        print("=" * 60)
        
        youtube = self.get_authenticated_service()
        if not youtube:
            print("ERROR: Could not authenticate with YouTube.")
            return

        # Get recent videos
        print(f"Fetching recent {max_videos} videos from channel...")
        videos = self.get_channel_videos(youtube, max_videos)
        
        if not videos:
            print("ERROR: No videos found.")
            return

        print(f"Found {len(videos)} videos to check.")
        print("-" * 60)

        processed_count = 0
        for i, video in enumerate(videos, 1):
            video_id = video["video_id"]
            title = video["title"]
            
            print(f"[{i}/{len(videos)}] Checking: '{title}'")
            
            # Get video details
            details = self.get_video_details(youtube, video_id)
            if not details:
                print(f"  ERROR: Could not get video details. Skipping.")
                continue

            # Skip private/unlisted videos
            if details["privacy_status"] != "public":
                print(f"  SKIP: Video is {details['privacy_status']}, not public.")
                continue

            # Check if it already has a pinned affiliate comment
            if self.has_pinned_comment_from_channel(youtube, video_id):
                print(f"  SKIP: Already has affiliate comment.")
                continue

            # Extract affiliate links from description
            affiliate_links = self.extract_affiliate_links_from_description(details["description"])
            
            if not affiliate_links:
                print(f"  SKIP: No affiliate links found in description.")
                continue

            # Post the affiliate comment
            print(f"  PROCESSING: Adding affiliate comment...")
            self.post_affiliate_comment(youtube, video_id, title, affiliate_links)
            processed_count += 1

            print()  # Add spacing between videos

        print("=" * 60)
        print(f"COMPLETE: Processed {processed_count} videos and added missing affiliate comments.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add missing affiliate comments to YouTube videos.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    parser.add_argument('--channel', type=str, required=True, help="Channel name for credential files.")
    parser.add_argument('--secrets-path', type=str, required=True, help="Path to the client_secret.json file.")
    parser.add_argument('--token-path', type=str, help="Path to the token .pickle file.")
    parser.add_argument('--max-videos', type=int, default=20, help="Maximum number of recent videos to check (default: 20).")
    
    args = parser.parse_args()

    try:
        print(f"Running Comment Manager for language '{args.language}'")
        Config = get_config(args.language)
        print(f"Loaded configuration for language: {Config.CONTENT_LANGUAGE}")

        # --- MODIFIED: Handle token path generation in the 'tokens' directory ---
        token_path = args.token_path
        if not token_path:
            # Use channel name directly for token path
            token_path = os.path.join('tokens', f"token_{args.channel}.pickle")

        # Create the comment manager
        manager = YouTubeCommentManager(Config, args.channel, args.secrets_path, token_path)
        manager.process_videos_missing_comments(args.max_videos)

    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1) 