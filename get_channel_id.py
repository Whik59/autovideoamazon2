#!/usr/bin/env python3
"""
Get YouTube Channel ID from @username URL
"""

import requests
import re
import json
import sys

def get_channel_id_from_username(username_url, api_key):
    """
    Get channel ID from @username URL using YouTube API search.
    """
    # Extract username from URL
    if '@' in username_url:
        username = username_url.split('@')[1].split('/')[0]
    else:
        username = username_url
    
    print(f"🔍 Looking for channel: @{username}")
    
    # Use YouTube API to search for the channel
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': username,
        'type': 'channel',
        'maxResults': 10,
        'key': api_key
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return None
    
    data = response.json()
    
    print(f"📋 Found {len(data.get('items', []))} channel results:")
    
    for i, item in enumerate(data.get('items', []), 1):
        channel_id = item['id']['channelId']
        channel_title = item['snippet']['title']
        channel_desc = item['snippet']['description'][:100] + '...'
        
        print(f"{i}. {channel_title}")
        print(f"   ID: {channel_id}")
        print(f"   Description: {channel_desc}")
        print()
        
        # If title matches closely, return this one
        if username.lower() in channel_title.lower() or channel_title.lower() in username.lower():
            print(f"✅ Best match found: {channel_title}")
            return channel_id
    
    # Return first result if no exact match
    if data.get('items'):
        best_match = data['items'][0]
        channel_id = best_match['id']['channelId']
        channel_title = best_match['snippet']['title']
        print(f"🎯 Using first result: {channel_title}")
        return channel_id
    
    return None

def get_api_key_from_credentials(credentials_file):
    """
    Extract API key from Google Cloud credentials file.
    Note: This won't work directly as client credentials are different from API keys.
    You need a separate YouTube Data API key.
    """
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        print("ℹ️  Note: The client credentials file doesn't contain a YouTube API key.")
        print("   You need to create a YouTube Data API key separately in Google Cloud Console.")
        print("   Project ID from credentials:", creds.get('installed', {}).get('project_id', 'Not found'))
        
        return None
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get YouTube channel ID from @username")
    parser.add_argument('username', help="YouTube @username or URL")
    parser.add_argument('--api-key', help="YouTube Data API v3 key")
    parser.add_argument('--credentials', help="Path to Google Cloud credentials file")
    
    args = parser.parse_args()
    
    # Try to get API key
    api_key = args.api_key
    
    if args.credentials and not api_key:
        print(f"📁 Checking credentials file: {args.credentials}")
        api_key = get_api_key_from_credentials(args.credentials)
    
    if not api_key:
        print("❌ YouTube Data API key required!")
        print("\n🔑 How to get an API key:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project (or create new)")
        print("3. Enable 'YouTube Data API v3'")
        print("4. Go to Credentials → Create Credentials → API Key")
        print("5. Copy the API key")
        print("\n💡 Usage:")
        print(f"   python get_channel_id.py '{args.username}' --api-key YOUR_API_KEY")
        sys.exit(1)
    
    channel_id = get_channel_id_from_username(args.username, api_key)
    
    if channel_id:
        print(f"\n🎉 Channel ID found: {channel_id}")
        print(f"📺 You can now use: python youtube_channel_scraper.py {channel_id} --api-key {api_key}")
    else:
        print("❌ Channel ID not found") 