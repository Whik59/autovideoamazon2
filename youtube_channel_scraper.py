#!/usr/bin/env python3
"""
YouTube Channel Video Title Scraper

This script extracts all video titles from a YouTube channel.
Supports multiple methods: YouTube API (recommended) and web scraping (backup).
"""

import os
import json
import argparse
import requests
from datetime import datetime
import time

# YouTube API method (requires API key)
def get_videos_with_api(channel_id, api_key, max_results=None):
    """
    Get all video titles from a YouTube channel using the official API.
    
    Args:
        channel_id: YouTube channel ID (starts with UC...)
        api_key: YouTube Data API v3 key
        max_results: Maximum number of videos to fetch (None for all)
    
    Returns:
        List of dictionaries with video information
    """
    videos = []
    next_page_token = None
    page_count = 0
    
    print(f"🔍 Fetching videos from channel: {channel_id}")
    
    while True:
        # Get channel uploads playlist ID
        if page_count == 0:
            channel_url = f"https://www.googleapis.com/youtube/v3/channels"
            channel_params = {
                'part': 'contentDetails,snippet',
                'id': channel_id,
                'key': api_key
            }
            
            response = requests.get(channel_url, params=channel_params)
            if response.status_code != 200:
                print(f"❌ Error fetching channel info: {response.status_code}")
                print(f"Response: {response.text}")
                return []
            
            channel_data = response.json()
            if not channel_data.get('items'):
                print(f"❌ Channel not found: {channel_id}")
                return []
            
            channel_info = channel_data['items'][0]
            channel_name = channel_info['snippet']['title']
            uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            print(f"📺 Channel: {channel_name}")
            print(f"📋 Uploads playlist: {uploads_playlist_id}")
        
        # Get videos from uploads playlist
        playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            'part': 'snippet',
            'playlistId': uploads_playlist_id,
            'maxResults': 50,  # Max per request
            'key': api_key
        }
        
        if next_page_token:
            params['pageToken'] = next_page_token
        
        response = requests.get(playlist_url, params=params)
        if response.status_code != 200:
            print(f"❌ Error fetching videos: {response.status_code}")
            break
        
        data = response.json()
        page_videos = []
        
        for item in data.get('items', []):
            snippet = item['snippet']
            video_info = {
                'title': snippet['title'],
                'video_id': snippet['resourceId']['videoId'],
                'published_at': snippet['publishedAt'],
                'description': snippet.get('description', '')[:200] + '...',  # First 200 chars
                'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', ''),
                'url': f"https://www.youtube.com/watch?v={snippet['resourceId']['videoId']}"
            }
            page_videos.append(video_info)
        
        videos.extend(page_videos)
        page_count += 1
        
        print(f"📄 Page {page_count}: Found {len(page_videos)} videos (Total: {len(videos)})")
        
        # Check if we should continue
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
        
        if max_results and len(videos) >= max_results:
            videos = videos[:max_results]
            break
        
        # Rate limiting
        time.sleep(0.1)
    
    print(f"✅ Total videos found: {len(videos)}")
    return videos

def get_channel_id_from_url(channel_url):
    """
    Extract channel ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/channel/UC...
    - https://www.youtube.com/@username
    - https://www.youtube.com/c/channelname
    - https://www.youtube.com/user/username
    """
    if '/channel/' in channel_url:
        return channel_url.split('/channel/')[1].split('?')[0].split('/')[0]
    
    # For @username, /c/, /user/ we'd need additional API calls or web scraping
    # For now, return the input and let the user know
    print("⚠️  For @username, /c/, or /user/ URLs, please find the channel ID manually.")
    print("   You can find it by viewing page source and looking for 'channelId'")
    return channel_url

def save_results(videos, channel_id, output_format='json'):
    """
    Save the results to a file.
    
    Args:
        videos: List of video dictionaries
        channel_id: Channel ID for filename
        output_format: 'json', 'csv', or 'txt'
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format == 'json':
        filename = f"youtube_videos_{channel_id}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'channel_id': channel_id,
                'scraped_at': datetime.now().isoformat(),
                'total_videos': len(videos),
                'videos': videos
            }, f, indent=2, ensure_ascii=False)
    
    elif output_format == 'csv':
        filename = f"youtube_videos_{channel_id}_{timestamp}.csv"
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'Video ID', 'Published At', 'URL', 'Description'])
            for video in videos:
                writer.writerow([
                    video['title'],
                    video['video_id'],
                    video['published_at'],
                    video['url'],
                    video['description']
                ])
    
    elif output_format == 'txt':
        filename = f"youtube_videos_{channel_id}_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"YouTube Channel Videos - {channel_id}\n")
            f.write(f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total videos: {len(videos)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, video in enumerate(videos, 1):
                f.write(f"{i:3d}. {video['title']}\n")
                f.write(f"     Published: {video['published_at'][:10]}\n")
                f.write(f"     URL: {video['url']}\n")
                f.write(f"     Description: {video['description']}\n\n")
    
    print(f"💾 Results saved to: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="Extract all video titles from a YouTube channel")
    parser.add_argument('channel', help="YouTube channel ID (UC...) or channel URL")
    parser.add_argument('--api-key', help="YouTube Data API v3 key (get from Google Cloud Console)")
    parser.add_argument('--max-results', type=int, help="Maximum number of videos to fetch")
    parser.add_argument('--output', choices=['json', 'csv', 'txt'], default='json', 
                       help="Output format (default: json)")
    parser.add_argument('--titles-only', action='store_true', 
                       help="Print only titles to console (no file output)")
    
    args = parser.parse_args()
    
    # Extract channel ID if URL provided
    channel_id = args.channel
    if 'youtube.com' in channel_id:
        channel_id = get_channel_id_from_url(channel_id)
    
    print(f"🚀 YouTube Channel Video Scraper")
    print(f"📺 Channel ID: {channel_id}")
    
    # Check for API key
    api_key = args.api_key or os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ YouTube API key required!")
        print("   Get one from: https://console.cloud.google.com/")
        print("   Enable YouTube Data API v3")
        print("   Usage: python youtube_channel_scraper.py CHANNEL_ID --api-key YOUR_KEY")
        print("   Or set environment variable: YOUTUBE_API_KEY=your_key")
        return
    
    # Fetch videos
    videos = get_videos_with_api(channel_id, api_key, args.max_results)
    
    if not videos:
        print("❌ No videos found or error occurred")
        return
    
    # Output results
    if args.titles_only:
        print(f"\n📋 Video Titles ({len(videos)} videos):")
        print("=" * 60)
        for i, video in enumerate(videos, 1):
            print(f"{i:3d}. {video['title']}")
    else:
        # Save to file
        filename = save_results(videos, channel_id, args.output)
        
        # Also show first few titles
        print(f"\n📋 First 10 video titles:")
        print("=" * 60)
        for i, video in enumerate(videos[:10], 1):
            published = video['published_at'][:10]
            print(f"{i:2d}. {video['title']} ({published})")
        
        if len(videos) > 10:
            print(f"... and {len(videos) - 10} more videos")
        
        print(f"\n💾 Full results saved to: {filename}")

if __name__ == "__main__":
    main() 