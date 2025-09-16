#!/usr/bin/env python3
"""
Amazon Keyword Expander

This script takes a base list of keywords, queries the Amazon search suggestion
API for each one, and generates an expanded list of long-tail keywords.
"""

import requests
import json
import time
import argparse
import os
import random

# The official endpoint for Amazon's search suggestions
AMAZON_SUGGESTION_URL = "https://www.amazon.fr/s/suggestion"

# A common browser User-Agent to make requests look legitimate
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_suggestions(keyword, marketplace_id=4):
    """
    Fetches search suggestions for a given keyword from Amazon.

    Args:
        keyword (str): The keyword to get suggestions for.
        marketplace_id (int): The ID for the Amazon marketplace (4 for France).

    Returns:
        list: A list of keyword suggestions, or an empty list if an error occurs.
    """
    params = {
        'k': keyword,
        'alias': 'aps',
        'c': '1',
        'mkt': str(marketplace_id),
        's': '126,131,130,129',
        'x': '17'
    }
    try:
        response = requests.get(AMAZON_SUGGESTION_URL, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # The new response is a JSON object with a 'suggestions' key
        data = response.json()
        if 'suggestions' in data and isinstance(data['suggestions'], list):
            # Extract the 'value' from each suggestion object
            return [s['value'] for s in data['suggestions']]
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not fetch suggestions for '{keyword}': {e}")
    except json.JSONDecodeError:
        print(f"  [ERROR] Could not decode JSON response for '{keyword}'. Amazon might be blocking requests.")
    return []

def main():
    parser = argparse.ArgumentParser(description="Expand an Amazon keyword list using search suggestions.")
    parser.add_argument('input_file', help="Path to the input file with base keywords (e.g., amazon.txt).")
    parser.add_argument('--output-file', default='amazon_expanded.txt', help="Path to save the expanded keyword list.")
    parser.add_argument('--lang', default='fr', help="Amazon country TLD to use (e.g., fr, de, com).")
    parser.add_argument('--delay', type=float, default=1.5, help="Base delay in seconds between requests.")
    
    args = parser.parse_args()

    marketplace_map = {
        'fr': 4, 'de': 5, 'es': 7, 'it': 8, 'co.uk': 3, 'com': 1
    }

    if args.lang not in marketplace_map:
        print(f"Error: Unsupported language '{args.lang}'. Supported: {', '.join(marketplace_map.keys())}")
        return

    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found at '{args.input_file}'")
        return

    print(f"🚀 Starting Amazon Keyword Expander...")
    print(f"📘 Reading base keywords from: {args.input_file}")
    
    with open(args.input_file, 'r', encoding='utf-8') as f:
        base_keywords = {line.strip() for line in f if line.strip() and not line.startswith('#')}

    print(f"  - Found {len(base_keywords)} unique base keywords.")
    
    all_keywords = set(base_keywords)
    total_base_keywords = len(base_keywords)

    print(f"\n🔍 Fetching suggestions from Amazon.{args.lang}...")

    for i, keyword in enumerate(list(base_keywords), 1):
        print(f"  ({i}/{total_base_keywords}) Processing: '{keyword}'")
        
        suggestions = fetch_suggestions(keyword, marketplace_map[args.lang])
        
        if suggestions:
            print(f"    -> Found {len(suggestions)} new suggestions.")
            all_keywords.update(suggestions)
        
        # --- Crucial Step: Wait to avoid being blocked ---
        # Add a small random jitter to the delay to make it less robotic
        sleep_time = args.delay + random.uniform(0, 0.5)
        time.sleep(sleep_time)

    print("\n✅ Expansion complete.")
    
    sorted_keywords = sorted(list(all_keywords))
    
    print(f"  - Initial keywords: {len(base_keywords)}")
    print(f"  - Total unique keywords found: {len(sorted_keywords)}")
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        for kw in sorted_keywords:
            f.write(kw + '\n')
            
    print(f"\n💾 Saved {len(sorted_keywords)} keywords to: {args.output_file}")

if __name__ == "__main__":
    main() 