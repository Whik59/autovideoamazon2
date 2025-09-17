import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import urljoin
import json
import os
import shutil
import subprocess
import concurrent.futures
import threading
import sys

# Fix Windows console encoding issues
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows console
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Fallback: Replace problematic Unicode characters
        pass

def safe_print(message):
    """Print message with Unicode characters replaced for Windows compatibility"""
    if sys.platform == "win32":
        # Replace problematic Unicode characters with safe alternatives
        replacements = {
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🔄': '[RETRY]',
            '▶️': '[RUNNING]',
            '🖼️': '[IMAGE]',
            '🎬': '[VIDEO]',
            '⏭️': '[SKIP]'
        }
        for unicode_char, replacement in replacements.items():
            message = message.replace(unicode_char, replacement)
    print(message)

class AmazonScraper:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.base_url = f"https://www.amazon.{self.config.AMAZON_TLD}"
        self.seen_video_ids_lock = threading.Lock()
        
        # Set session headers and cookies for better compatibility
        self.session.headers.update({
            'User-Agent': random.choice(self.config.USER_AGENTS),
            'Accept-Language': f'{self.config.CONTENT_LANGUAGE}-{self.config.AMAZON_TLD.upper()},'
                               f'{self.config.CONTENT_LANGUAGE};q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        # Add cookies to look more legitimate
        self.session.cookies.update({
            'session-id': '262-1234567-1234567',
            'ubid-acbfr': '262-1234567-1234567',
            'i18n-prefs': 'EUR',
            f'lc-acbfr': f'{self.config.TTS_LANGUAGE_CODE.replace("-", "_")}',
            'sp-cdn': f'L5Z9:{self.config.AMAZON_TLD.upper()}',
        })
        
        # Directories are now created by the pipeline orchestrator.
        # This script assumes they exist.
        os.makedirs(self.config.IMAGES_DIR, exist_ok=True)
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.config.VIDEOS_DIR, exist_ok=True)
        
    def make_request(self, url, retries=3):
        """Make HTTP request with retries and CAPTCHA detection"""
        for attempt in range(retries):
            try:
                # Random delay to appear human
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                # Check for CAPTCHA
                if 'validateCaptcha' in response.text or 'Continuer les achats' in response.text:
                    safe_print(f"  ⚠️ CAPTCHA detected on attempt {attempt + 1}")
                    if attempt < retries - 1:
                        safe_print("  🔄 Waiting longer before retry...")
                        time.sleep(random.uniform(10, 15))
                        continue
                    else:
                        safe_print("  ❌ All attempts failed due to CAPTCHA")
                        return None
                
                return response
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    safe_print(f"Status 503, retrying...")
                    if attempt < retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                safe_print(f"  ⚠️ Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(5, 8))
            except Exception as e:
                safe_print(f"  ⚠️ Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(5, 8))
        
        return None
    
    def search_products(self, keyword, page=1):
        """Search for products on Amazon with pagination and a price filter."""
        # Add price filter to the URL to only get products above 50 EUR/USD/etc.
        search_url = f"{self.base_url}/s?k={keyword.replace(' ', '+')}&page={page}&low-price=50&ref=sr_pg_{page}"
        
        safe_print(f"🔍 Searching: {search_url}")
        
        response = self.make_request(search_url, retries=5)
        if not response:
            safe_print("❌ Failed to get search results")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find product containers
        containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        if not containers:
            containers = soup.find_all('div', class_=re.compile(r's-result-item'))
        
        safe_print(f"✅ Found {len(containers)} product containers")
        
        products = []
        for container in containers:  # Get all products from this page
            product = self.extract_product_info(container)
            if product:
                products.append(product)
                title_short = product['title'][:50] + "..." if len(product['title']) > 50 else product['title']
                safe_print(f"✅ Product {len(products)}: {title_short}")
        
        return products
    
    def extract_product_info(self, container):
        """Extract basic product information from search result"""
        try:
            # Skip sponsored products
            if container.find('span', string=re.compile(r'Sponsorisé|Sponsored|Gesponsert', re.I)):
                return None
            
            product = {}
            
            # Title and URL - try multiple selectors
            title_elem = None
            link = None
            
            # Method 1: Look for h2 with product title
            h2_elements = container.find_all('h2')
            for h2 in h2_elements:
                link = h2.find('a')
                if link and link.get('href'):
                    title_elem = h2
                    break
            
            # Method 2: Look for any link with product title
            if not title_elem:
                links = container.find_all('a', href=re.compile(r'/dp/'))
                for potential_link in links:
                    if potential_link.get_text().strip():
                        link = potential_link
                        title_elem = potential_link
                        break
            
            # Method 3: Look for span with product title
            if not title_elem:
                spans = container.find_all('span')
                for span in spans:
                    parent_link = span.find_parent('a')
                    if parent_link and parent_link.get('href') and '/dp/' in parent_link.get('href'):
                        link = parent_link
                        title_elem = span
                        break
            
            if link and link.get('href'):
                title_text = link.get_text().strip() or title_elem.get_text().strip()
                if title_text and len(title_text) > 10:  # Valid title
                    product['title'] = title_text
                    href = link.get('href')
                    if href.startswith('/'):
                        product['url'] = urljoin(self.base_url, href)
                    else:
                        product['url'] = href
                    
                    # Extract ASIN
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', product['url'])
                    if asin_match:
                        product['asin'] = asin_match.group(1)
            
            # Price - IMPROVED extraction to get complete price
            price_text = ""
            
            # Method 1: Look for complete price structure (whole + fraction + currency)
            price_range = container.find('span', class_='a-price-range')
            if price_range:
                price_text = price_range.get_text().strip()
            else:
                # Method 2: Combine whole and fraction parts
                whole_elem = container.find('span', class_='a-price-whole')
                fraction_elem = container.find('span', class_='a-price-fraction')
                currency_elem = container.find('span', class_='a-price-symbol')
                
                if whole_elem:
                    price_text = whole_elem.get_text().strip()
                    if fraction_elem:
                        price_text += fraction_elem.get_text().strip()
                    if currency_elem:
                        price_text += currency_elem.get_text().strip()
                
                # Method 3: Look for offscreen price (complete price)
                if not price_text:
                    offscreen_elem = container.find('span', class_='a-offscreen')
                    if offscreen_elem:
                        price_text = offscreen_elem.get_text().strip()
                
                # Method 4: Search all spans for price pattern
                if not price_text:
                    price_spans = container.find_all('span')
                    for span in price_spans:
                        text = span.get_text().strip()
                        if re.search(r'\d+[,\.]\d*\s*€|€\s*\d+[,\.]\d*', text):
                            price_text = text
                            break
            
            if price_text:
                # Clean and standardize price format
                price_match = re.search(r'(\d+[,\.]\d*)\s*€|€\s*(\d+[,\.]\d*)', price_text)
                if price_match:
                    price_value = price_match.group(1) or price_match.group(2)
                    product['price'] = f"{price_value}€"
                else:
                    product['price'] = price_text
            else:
                product['price'] = "Prix non disponible"
            
            # Rating
            rating_elem = container.find('span', class_='a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+[,\.]\d*)', rating_text)
                if rating_match:
                    product['rating'] = float(rating_match.group(1).replace(',', '.'))
            
            # The price filter is now applied in the search URL, so the client-side check is no longer needed.

            # Filter by rating: Only accept products with 4.0 stars or more
            if product.get('rating', 0) < 4.0:
                title_for_log = product.get('title', 'Unknown product')
                safe_print(f"  🔻 Skipping '{title_for_log[:40]}...' (Rating: {product.get('rating', 'N/A')}/5)")
                return None
            
            # Main image
            img_elem = container.find('img', class_='s-image')
            if not img_elem:
                img_elem = container.find('img')
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    product['main_image'] = src
            
            # Debug output
            if product.get('title'):
                safe_print(f"  ✅ Extracted: {product['title'][:50]}...")
                return product
            else:
                return None
            
        except Exception as e:
            safe_print(f"❌ Error extracting product: {str(e)}")
            return None
    
    def get_full_product_details(self, product):
        """
        Loads a product page ONCE, finds all valid videos, and applies selection logic.
        - Priority 1: Take the single longest video if its duration is >= 25s.
        - Priority 2: If not, take the two longest videos if they are both < 25s.
        - Otherwise, reject the product.
        Only if a valid video combination is found does it proceed to scrape other details.
        """
        safe_print(f"  📝 Getting full details for: {product['title'][:40]}...")
        
        response = self.make_request(product['url'])
        if not response:
            safe_print("  ❌ Failed to get product page")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Find ALL candidate videos first
        candidate_videos = []
        processed_video_ids = set() # Prevents adding the same video twice from one page
        
        # Method 1: Look for video IDs in JSON data
        video_id_pattern = r'"mediaObjectId":"([a-f0-9]+)"'
        video_ids = sorted(list(set(re.findall(video_id_pattern, response.text))))
        
        for video_id in video_ids:
            if video_id in processed_video_ids:
                continue

            duration_pattern = rf'"mediaObjectId":"{video_id}"[^}}]*"durationTimestamp":"([^"]+)"'
            duration_match = re.search(duration_pattern, response.text)
            duration_str = duration_match.group(1) if duration_match else '0:00'
            duration_seconds = self._get_video_duration_seconds(duration_str)

            if duration_seconds > 0:
                video_url_pattern = rf'"mediaObjectId":"{video_id}"[^}}]*"url":"([^"]+)"'
                video_url_match = re.search(video_url_pattern, response.text)
                if video_url_match:
                    video_url = video_url_match.group(1).replace('\\\\/', '/')
                    if self._is_video_aspect_ratio_valid(video_url):
                        title_pattern = rf'"mediaObjectId":"{video_id}"[^}}]*"title":"([^"]+)"'
                        title_match = re.search(title_pattern, response.text)
                        title = title_match.group(1) if title_match else 'Product Video'
                        candidate_videos.append({'url': video_url, 'title': title, 'duration': duration_seconds, 'video_id': video_id, 'type': 'hls'})
                        processed_video_ids.add(video_id)

        # Method 2: Look for videos JSON array
        video_array_pattern = r'"videos":\s*(\[.+?\])'
        video_array_matches = re.findall(video_array_pattern, response.text, re.IGNORECASE)
        for match in video_array_matches:
            try:
                videos_data = json.loads(match)
                for video in videos_data:
                    duration_str = video.get('durationTimestamp', '0:00')
                    duration_seconds = self._get_video_duration_seconds(duration_str)
                    
                    media_id = video.get('mediaObjectId', f"json_array_{len(candidate_videos)}")
                    if media_id in processed_video_ids:
                        continue

                    if duration_seconds > 0:
                        url = video.get('url', '')
                        if url and self._is_video_aspect_ratio_valid(url):
                            title = video.get('title', 'Product Video')
                            candidate_videos.append({'url': url, 'title': title, 'duration': duration_seconds, 'video_id': media_id, 'type': 'hls'})
                            processed_video_ids.add(media_id)
            except json.JSONDecodeError:
                continue

        if not candidate_videos:
            safe_print("  ❌ No videos found on page.")
            return None

        # 2. Apply the selection logic
        long_videos = [v for v in candidate_videos if v['duration'] >= 25]
        short_videos = [v for v in candidate_videos if v['duration'] < 25]

        long_videos.sort(key=lambda x: x['duration'], reverse=True)
        short_videos.sort(key=lambda x: x['duration'], reverse=True)

        selected_videos = []
        if long_videos:
            selected_videos.append(long_videos[0])
            safe_print(f"  ✅ Found a valid video with duration >= 25s ({long_videos[0]['duration']}s).")
        elif len(short_videos) >= 2:
            selected_videos.extend(short_videos[:2])
            durations = [v['duration'] for v in selected_videos]
            safe_print(f"  ✅ Found two short videos to combine (durations: {durations}s).")
        else:
            safe_print(f"  ❌ No suitable video combination found. Found {len(long_videos)} long and {len(short_videos)} short videos.")
            return None

        # 3. If videos are selected, proceed to extract all other details
        product['videos_data'] = selected_videos
        product['has_video'] = True
        safe_print("  ✅ Video combination found. Now extracting other details from the same page...")
        
        images = re.findall(r'"hiRes":"([^"]+)"', response.text) or re.findall(r'"large":"([^"]+)"', response.text)
        product['image'] = images[0] if images else product.get('main_image')
        safe_print(f"  ✅ Found product image")

        descriptions = []
        about_heading = soup.find(['h2', 'h3'], string=re.compile(self.config.ABOUT_THIS_ITEM_LABEL, re.I))
        if about_heading:
            feature_list = about_heading.find_next_sibling('ul')
            if feature_list:
                items = feature_list.find_all('li')
                for item in items:
                    text = re.sub(r'\s+', ' ', item.get_text(strip=True))
                    if (text and len(text) > 20 and not any(skip in text.lower() for skip in ['asin', 'dimensions', 'poids', 'fabricant', 'numéro du modèle'])):
                        descriptions.append(text)
        
        product['description'] = descriptions[:10]
        safe_print(f"  ✅ Extracted {len(product['description'])} high-quality description points.")
        
        brand_elem = soup.find('a', {'id': 'bylineInfo'})
        if brand_elem:
            product['brand'] = brand_elem.get_text(strip=True)
            safe_print(f"  ✅ Brand: {product['brand'][:30]}")

        # 3. Generate conversion signals
        safe_print(f"  🎯 Generating conversion signals...")
        conversion_data = {'urgency_indicators': [], 'authority_signals': []}
        rating = product.get('rating', 0)
        price_str = product.get('price', '0€')
        price_num = float(re.search(r'(\d+[,.]?\d*)', price_str.replace(',', '.')).group(1)) if re.search(r'(\d+[,.]?\d*)', price_str) else 0
        
        if rating >= 4.5:
            conversion_data['urgency_indicators'].append("🔥 Hot seller - order fast!")
            conversion_data['authority_signals'].append("⭐ Amazon's Choice")
        elif rating >= 4.0:
            conversion_data['urgency_indicators'].append("📈 Popular choice - selling fast")
            conversion_data['authority_signals'].append("👑 Highly rated by customers")
        
        if price_num < 50: conversion_data['urgency_indicators'].append("💸 Incredible deal under 50€")
        elif price_num > 150: conversion_data['urgency_indicators'].append("🏆 Premium quality investment")
        
        product['conversion_data'] = conversion_data
        safe_print(f"  ✅ Conversion signals generated")
        
        return product
    
    def _get_video_duration_seconds(self, duration_str, max_seconds=120):
        """
        Parses a duration string (e.g., '1:35') and returns the total seconds.
        Returns 0 if the duration is invalid or outside the 0-max_seconds range.
        """
        try:
            parts = list(map(int, duration_str.split(':')))
            seconds = 0
            if len(parts) == 3: seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2: seconds = parts[0] * 60 + parts[1]
            else: return 0

            if 0 < seconds <= max_seconds:
                return seconds
            else:
                # This is noisy, let's only print rejections for aspect ratio
                # print(f"    ❌ Duration ({duration_str}) is over the {max_seconds}s limit. Skipping.")
                return 0
        except (ValueError, IndexError):
            # print(f"    ⚠️ Could not parse duration: {duration_str}")
            return 0

    def _is_video_aspect_ratio_valid(self, video_url):
        """Checks if a video has a 16:9 aspect ratio using ffprobe."""
        try:
            safe_print(f"    📏 Checking aspect ratio for video...")
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=s=x:p=0',
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding='utf-8')
            
            if result.returncode == 0 and result.stdout.strip():
                width, height = map(int, result.stdout.strip().split('x'))
                
                # --- START: Stricter Aspect Ratio Check ---
                # Reject if video is square or vertical
                if width <= height:
                    safe_print(f"    ❌ REJECTED: Video is square or vertical ({width}x{height}). Only horizontal videos accepted.")
                    return False
                
                aspect_ratio = width / height
                
                # Reject videos that are too narrow (close to square)
                if aspect_ratio < 1.3:
                    safe_print(f"    ❌ REJECTED: Video aspect ratio is too narrow ({width}x{height}, ratio: {aspect_ratio:.2f}). Minimum ratio: 1.3")
                    return False
                
                # Check if it's close to 16:9 (approx 1.777) or other acceptable widescreen ratios
                target_ratio = 16/9  # 1.777
                if abs(aspect_ratio - target_ratio) < 0.2:  # More tolerant for 16:9
                    safe_print(f"    ✅ ACCEPTED: Aspect ratio {width}x{height} (ratio: {aspect_ratio:.2f}) is suitable for 16:9 processing.")
                    return True
                elif aspect_ratio > 1.5:  # Accept other widescreen formats
                    safe_print(f"    ✅ ACCEPTED: Widescreen aspect ratio {width}x{height} (ratio: {aspect_ratio:.2f}) can be processed.")
                    return True
                else:
                    safe_print(f"    ❌ REJECTED: Aspect ratio {width}x{height} (ratio: {aspect_ratio:.2f}) is not suitable for horizontal video processing.")
                    return False
                # --- END: Stricter Aspect Ratio Check ---
            else:
                safe_print(f"    ⚠️ Could not determine aspect ratio. Assuming it's valid.")
                # If ffprobe fails, we cautiously accept the video.
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            safe_print(f"    ⚠️ FFprobe error checking aspect ratio: {str(e)[:100]}. Assuming valid.")
            return True # Cautiously accept if ffprobe fails

    def _is_video_duration_valid(self, duration_str, max_seconds=120):
        """Checks if video duration is within the allowed limit (default 2 minutes)."""
        try:
            parts = list(map(int, duration_str.split(':')))
            seconds = 0
            if len(parts) == 3: seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2: seconds = parts[0] * 60 + parts[1]
            else: return False

            if 0 < seconds <= max_seconds:
                safe_print(f"    ✅ Duration ({duration_str}) is within the 2-minute limit.")
                return True
            else:
                safe_print(f"    ❌ Duration ({duration_str}) is not suitable. Skipping.")
                return False
        except (ValueError, IndexError):
            safe_print(f"    ⚠️ Could not parse duration: {duration_str}")
            return False

    def check_product_video(self, product):
        """Quick check if product has a suitable video (under 2 minutes)."""
        safe_print(f"  🔍 Checking for video...")
        
        response = self.make_request(product['url'])
        if not response:
            safe_print("  ❌ Failed to load product page")
            product['has_video'] = False
            return product
        
        # Method 1: Look for video IDs in JSON data
        video_id_pattern = r'"mediaObjectId":"([a-f0-9]+)"'
        # Use a set to get unique video IDs, then sort to maintain order
        video_ids = sorted(list(set(re.findall(video_id_pattern, response.text))))
        
        if video_ids:
            safe_print(f"    Found {len(video_ids)} potential video IDs. Checking each...")

        # Iterate through ALL found video IDs to find one with a valid duration
        for video_id in video_ids:
            duration_pattern = rf'"mediaObjectId":"{video_id}"[^}}]*"durationTimestamp":"([^"]+)"'
            duration_match = re.search(duration_pattern, response.text)
            duration = duration_match.group(1) if duration_match else '0:00'
            
            # If a suitable video is found, get all its data and return
            if self._is_video_duration_valid(duration):
                video_url_pattern = rf'"mediaObjectId":"{video_id}"[^}}]*"url":"([^"]+)"'
                video_url_match = re.search(video_url_pattern, response.text)
                
                if video_url_match:
                    video_url = video_url_match.group(1).replace('\\\\/', '/')
                    title_pattern = rf'"mediaObjectId":"{video_id}"[^}}]*"title":"([^"]+)"'
                    title_match = re.search(title_pattern, response.text)
                    title = title_match.group(1) if title_match else 'Product Video'
                    
                    product['video_data'] = {
                        'url': video_url,
                        'title': title,
                        'duration': duration,
                        'video_id': video_id,
                        'type': 'hls'
                    }
                    product['has_video'] = True
                    safe_print(f"  ✅ Found suitable HLS video: {title[:30]}... ({duration})")
                    return product # Success, we found a good video
        
        # Method 2: Look for videos JSON array
        video_array_pattern = r'"videos":\s*(\[.+?\])'
        video_array_matches = re.findall(video_array_pattern, response.text, re.IGNORECASE)
        
        if video_array_matches:
            safe_print(f"    Found {len(video_array_matches)} video JSON arrays. Checking each...")

        for match in video_array_matches:
            try:
                videos_data = json.loads(match)
                # Iterate through ALL videos in the JSON array
                for video in videos_data:
                    duration = video.get('durationTimestamp', '0:00')

                    # If a suitable video is found, get its data and return
                    if self._is_video_duration_valid(duration):
                        title = video.get('title', 'Product Video')
                        url = video.get('url', '')
                        media_id = video.get('mediaObjectId', 'json_array_0')
                        
                        if url:
                            product['video_data'] = {
                                'url': url,
                                'title': title,
                                'duration': duration,
                                'video_id': media_id,
                                'type': 'hls'
                            }
                            product['has_video'] = True
                            safe_print(f"  ✅ Found suitable JSON array video: {title[:30]}... ({duration})")
                            return product # Success, we found a good video
                        
            except json.JSONDecodeError:
                continue
        
        # No suitable videos found after checking all sources
        product['has_video'] = False
        product['video_data'] = None
        safe_print("  ❌ No suitable video found after checking all sources.")
        return product
    
    def convert_hls_to_mp4(self, hls_url, output_path, timeout=180):
        """Convert HLS stream to MP4 using ffmpeg with increased timeout and better headers."""
        try:
            safe_print(f"    🎬 Converting HLS to MP4 (timeout set to {timeout}s)...")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Use ffmpeg to convert HLS to MP4
            cmd = [
                'ffmpeg',
                '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-i', hls_url,
                '-c', 'copy',
                '-bsf:a', 'aac_adtstoasc',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding='utf-8')
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    safe_print(f"    ✅ Converted to MP4 ({size_mb:.1f} MB)")
                    return True
                else:
                    safe_print(f"    ❌ Output file not created")
                    return False
            else:
                safe_print(f"    ❌ FFmpeg error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            safe_print(f"    ❌ Timeout converting video")
            return False
        except FileNotFoundError:
            safe_print("    ❌ FFmpeg not found. Please install FFmpeg first.")
            return False
        except Exception as e:
            safe_print(f"    ❌ Error converting video: {str(e)}")
            return False
    
    def download_media(self, product, index):
        """Download video and first image for a product"""
        # Create directory for this product - IMPROVED safe name handling
        safe_name = re.sub(r'[^\w\s-]', '', product['title'])  # Remove special chars
        safe_name = re.sub(r'\s+', ' ', safe_name).strip()     # Clean up spaces
        safe_name = safe_name.replace(' ', '_')                # Replace spaces with underscores
        safe_name = safe_name[:30]                             # Limit length
        
        product_dir = os.path.join(self.config.VIDEOS_DIR, f"{index}_{safe_name}")
        
        # Ensure directory exists
        try:
            os.makedirs(product_dir, exist_ok=True)
            safe_print(f"  📁 Created directory: {product_dir}")
        except Exception as e:
            safe_print(f"  ❌ Error creating directory: {str(e)}")
            # Fallback to simpler directory name
            product_dir = os.path.join(self.config.VIDEOS_DIR, f"product_{index}")
            os.makedirs(product_dir, exist_ok=True)
            safe_print(f"  📁 Using fallback directory: {product_dir}")
        
        downloaded_files = []
        
        # Download first image for comparison table
        if product.get('image'):
            try:
                safe_print(f"  🖼️ Downloading product image...")
                response = self.make_request(product['image'])
                if response:
                    image_path = os.path.join(product_dir, f"product_image_{index}.jpg")
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    downloaded_files.append(('image', image_path))
                    safe_print(f"  ✅ Downloaded product image")
                else:
                    safe_print(f"  ❌ Failed to download product image")
            except Exception as e:
                safe_print(f"  ❌ Error downloading image: {str(e)}")
        
        # Download and convert videos
        if product.get('videos_data'):
            videos_data = product['videos_data'] # This is now a list
            for i, video_data in enumerate(videos_data, 1):
                try:
                    safe_print(f"  🎬 Processing video {i}/{len(videos_data)}: {video_data['title'][:30]}...")
                    
                    if video_data['type'] == 'hls':
                        # Suffix for multiple videos of the same product
                        video_path = os.path.join(product_dir, f"video_{i}_{video_data['video_id']}.mp4")
                        if self.convert_hls_to_mp4(video_data['url'], video_path):
                            downloaded_files.append(('video', video_path))
                            safe_print(f"  ✅ HLS video {i} converted and saved")
                        else:
                            safe_print(f"  ❌ Failed to convert HLS video {i}")
                    else:
                        # Direct MP4 download
                        safe_print(f"  📥 Downloading MP4 video...")
                        response = self.make_request(video_data['url'])
                        if response:
                            video_path = os.path.join(product_dir, f"video_{i}_{video_data['video_id']}.mp4")
                            with open(video_path, 'wb') as f:
                                f.write(response.content)
                            downloaded_files.append(('video', video_path))
                            safe_print(f"  ✅ Downloaded MP4 video {i}")
                        else:
                            safe_print(f"  ❌ Failed to download MP4 video {i}")
                            
                except Exception as e:
                    safe_print(f"  ❌ Error processing video {i}: {str(e)}")
        
        product['downloaded_files'] = downloaded_files
        return product
    
    def scrape_products(self, keyword):
        """Main scraping function"""
        safe_print(f"🚀 Starting scrape for: {keyword}")
        safe_print("=" * 60)
        
        products_to_process = []
        seen_video_ids = set() # Set to store video IDs of products already added
        processed_count = 0
        page = 1
        
        # Keep searching until we get the required number of products with videos
        while len(products_to_process) < self.config.PRODUCTS_PER_KEYWORD and page <= 5:  # Max 3 pages
            safe_print(f"\n🔍 Searching page {page} for products with videos...")
            
            # Search for products on current page
            products_on_page = self.search_products(keyword, page)
            if not products_on_page:
                safe_print(f"❌ No products found on page {page}")
                break
            
            safe_print(f"✅ Found {len(products_on_page)} products on page {page}. Checking them in parallel (5 workers)...")
            
            # Check each product for videos in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_product = {executor.submit(self.get_full_product_details, product): product for product in products_on_page}
                
                for future in concurrent.futures.as_completed(future_to_product):
                    if len(products_to_process) >= self.config.PRODUCTS_PER_KEYWORD:
                        # We have enough products, we can cancel remaining futures
                        # Note: cancellation is not guaranteed, but it's a good practice
                        for f in future_to_product:
                            f.cancel()
                        break 
                        
                    try:
                        fully_detailed_product = future.result()
                        
                        if not fully_detailed_product:
                            continue # Skip if no video or details were found
                        
                        # Check for duplicate videos (thread-safe)
                        with self.seen_video_ids_lock:
                            video_ids = [v['video_id'] for v in fully_detailed_product.get('videos_data', [])]
                            has_seen_video = False
                            for vid in video_ids:
                                if vid in seen_video_ids:
                                    has_seen_video = True
                                    safe_print(f"⏭️ Skipping product: Duplicate video (ID: {vid}) detected across parallel checks.")
                                    break
                            
                            if has_seen_video:
                                continue
                            
                            # If no duplicates, add all new video IDs to the seen set
                            for vid in video_ids:
                                seen_video_ids.add(vid)
                        
                        processed_count += 1
                        fully_detailed_product['index'] = processed_count
                        products_to_process.append(fully_detailed_product)
                        safe_print(f"✅ SUCCESS: Found a valid product with video ({len(products_to_process)}/{self.config.PRODUCTS_PER_KEYWORD}). Title: {fully_detailed_product['title'][:40]}...")

                    except Exception as exc:
                        safe_print(f"  ❌ A product failed during detail fetching: {exc}")

            if len(products_to_process) < self.config.PRODUCTS_PER_KEYWORD:
                page += 1
            else:
                break
        
        if not products_to_process:
            safe_print("\n❌ No products with suitable videos found after searching. Exiting.")
            return []

        # If we found some products, but not enough, that's also a failure for this keyword.
        if len(products_to_process) < self.config.PRODUCTS_PER_KEYWORD:
            safe_print(f"\n❌ Found only {len(products_to_process)}/{self.config.PRODUCTS_PER_KEYWORD} products with videos. Skipping keyword.")
            return None # Return None to indicate failure to the main script

        # Step 2: Download media for all selected products in parallel
        safe_print(f"\n🚀 Found {len(products_to_process)} products. Downloading all media in parallel (2 workers)...")
        detailed_products_with_media = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_product = {executor.submit(self.download_media, product, product['index']): product for product in products_to_process}
            
            for future in concurrent.futures.as_completed(future_to_product):
                try:
                    product_with_media = future.result()
                    if product_with_media:
                        detailed_products_with_media.append(product_with_media)
                except Exception as exc:
                    safe_print(f"  ❌ A product failed during media download: {exc}")
        
        # Sort results by index to ensure correct order
        detailed_products_with_media.sort(key=lambda p: p['index'])
        
        # Save results
        output_file = os.path.join(self.config.OUTPUT_DIR, "product.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_products_with_media, f, indent=2, ensure_ascii=False)
        
        safe_print(f"\n💾 Results saved to: {output_file}")
        
        # Print summary
        self.print_summary(detailed_products_with_media, keyword)
        
        return detailed_products_with_media
    
    def print_summary(self, products, keyword):
        """Print scraping summary"""
        safe_print(f"\n🎉 SCRAPING COMPLETE for '{keyword}'")
        safe_print("=" * 60)
        
        for i, product in enumerate(products, 1):
            safe_print(f"\n{i}. {product['title']}")
            safe_print(f"   💰 Price: {product.get('price', 'N/A')}")
            safe_print(f"   ⭐ Rating: {product.get('rating', 'N/A')}/5")
            safe_print(f"   🎬 Video: {'✅' if product.get('videos_data') else '❌'} ({len(product.get('videos_data', []))} clips)")
            safe_print(f"   🖼️ Image: {'✅' if product.get('image') else '❌'}")
            safe_print(f"   📁 ASIN: {product.get('asin', 'N/A')}")
        
        videos_count = sum(len(p.get('videos_data', [])) for p in products)
        images_count = sum(1 for p in products if p.get('image'))
        
        safe_print(f"\n📊 SUMMARY:")
        safe_print(f"   Products found: {len(products)}")
        safe_print(f"   Videos found: {videos_count}")
        safe_print(f"   Images found: {images_count}")
        
        safe_print(f"\n🎉 SUCCESS! Scraped {len(products)} products")
        safe_print("Check the 'images/' and 'output/' folders for results")

if __name__ == "__main__":
    import sys
    import argparse
    from config import get_config

    parser = argparse.ArgumentParser(description="Standalone scraper for a single keyword and language.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    parser.add_argument('keyword', type=str, nargs='?', default=None, help="The keyword to scrape on Amazon (optional).")
    parser.add_argument('--channel', type=str, default=None, help="Channel name to load keywords from keywords/{language}/{channel}.txt (optional).")
    # --- NEW: Add arguments for session directories ---
    parser.add_argument('--output-dir', type=str, help="Override default output directory.")
    parser.add_argument('--audio-dir', type=str, help="Override default audio directory.")
    parser.add_argument('--videos-dir', type=str, help="Override default videos directory.")
    args = parser.parse_args()

    try:
        # --- NEW: Keyword handling ---
        keyword = args.keyword
        if not keyword:
            safe_print(f"📖 No keyword provided. Selecting a random keyword for language '{args.language}'.")
            
            # Try channel-specific keyword file first
            if args.channel:
                keyword_file_path = os.path.join("keywords", args.language, f"{args.channel}.txt")
                if os.path.exists(keyword_file_path):
                    with open(keyword_file_path, 'r', encoding='utf-8') as f:
                        keywords = [line.strip() for line in f if line.strip()]
                    if keywords:
                        keyword = random.choice(keywords)
                        safe_print(f"SUCCESS: Randomly selected keyword '{keyword}' from channel '{args.channel}'")
                    else:
                        safe_print(f"ERROR: No keywords found in {keyword_file_path}")
                        sys.exit(1)
                else:
                    safe_print(f"❌ Channel keyword file not found: {keyword_file_path}")
                    sys.exit(1)
            else:
                # Fallback to old method
                keyword_file = f"keywords_{args.language}.txt"
                if not os.path.exists(keyword_file):
                    safe_print(f"❌ Keyword file not found: {keyword_file}")
                    safe_print("   Please provide a keyword or use --channel parameter")
                    sys.exit(1)
                with open(keyword_file, 'r', encoding='utf-8') as f:
                    keywords = [line.strip() for line in f if line.strip()]
                if not keywords:
                    safe_print(f"ERROR: No keywords found in {keyword_file}")
                    sys.exit(1)
                keyword = random.choice(keywords)
                safe_print(f"SUCCESS: Randomly selected keyword: '{keyword}'")

        safe_print(f"RUNNING: Step 1 in standalone mode for language '{args.language}' and keyword: '{keyword}'")
        # Load the specified language configuration
        Config = get_config(args.language)
        safe_print(f"SUCCESS: Loaded configuration for Amazon TLD: '{Config.AMAZON_TLD}'")
        
        # --- NEW: Override config paths if provided ---
        if args.output_dir:
            Config.OUTPUT_DIR = args.output_dir
            safe_print(f"   Overriding OUTPUT_DIR: {Config.OUTPUT_DIR}")
        if args.audio_dir:
            Config.AUDIO_DIR = args.audio_dir
            # Note: Scraper doesn't use AUDIO_DIR, but we add for consistency
        if args.videos_dir:
            Config.VIDEOS_DIR = args.videos_dir
            safe_print(f"   Overriding VIDEOS_DIR: {Config.VIDEOS_DIR}")

        # Instantiate and run the scraper
        scraper = AmazonScraper(Config)
        scraped_data = scraper.scrape_products(keyword)
    
        # Exit with a special code if scraping did not yield enough results
        if scraped_data is None:
                safe_print("   -> Exiting with status code 10 (not enough products found).")
                sys.exit(10)
        # --- NEW: Also exit with code 10 if NO products were found ---
        if not scraped_data:
                safe_print("   -> Exiting with status code 10 (zero products found).")
                sys.exit(10)

    except ImportError as e:
        safe_print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        safe_print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1) 