import argparse
from step1_scraper import AmazonScraper
from step2_content import ContentGenerator
from step3_video_simple import SimpleVideoAssembler
from step4_thumbnail import ThumbnailGenerator
from step5_youtube_uploader import YouTubeUploader
from config import get_config
import sys
import os

def run_pipeline_for_keyword(language_code, keyword, Config, channel_name=None):
    """
    Encapsulates the video creation pipeline for a single keyword.
    """
    print(f"\n{'='*60}")
    print(f"🎬 Processing keyword: '{keyword}' in language '{language_code}'")
    print(f"{'='*60}")

    # === Step 1: Scrape Amazon Products ===
    print("\n--- Running Step 1: Scraping Amazon ---")
    scraper = AmazonScraper(Config)
    scraped_data = scraper.scrape_products(keyword)
    if scraped_data is None: # Use the specific None check for "not enough products"
        print(f"⏭️  Skipping '{keyword}': Not enough products with videos were found. Moving to next keyword.")
        return # Cleanly exit for this keyword

    if not scraped_data:
        print(f"❌ Scraping failed for '{keyword}'. Aborting this keyword.")
        return

    # === Step 2: Generate Content & Audio ===
    print("\n--- Running Step 2: Generating Content & Audio ---")
    content_generator = ContentGenerator(Config, channel_name=channel_name)
    # Pass both keyword and config to the run method
    content_generator.run(keyword=keyword)

    # === Step 3: Assemble Video ===
    print("\n--- Running Step 3: Assembling Video ---")
    video_assembler = SimpleVideoAssembler(Config)
    video_assembler.run()

    # === Step 4: Generate Thumbnail ===
    print("\n--- Running Step 4: Generating Thumbnail ---")
    thumbnail_generator = ThumbnailGenerator(Config)
    thumbnail_generator.generate_thumbnail()

    # === Step 5: Upload to YouTube ===
    print("\n--- Running Step 5: Uploading to YouTube ---")
    youtube_uploader = YouTubeUploader(Config)
    youtube_uploader.upload_video()
    
    print(f"\n🎉 Video creation process for '{keyword}' in '{language_code}' completed successfully!")

def main(language_code, keyword, channel_name=None):
    """
    Main function to run the video creation pipeline for a specific language and keyword(s).
    """
    
    print(f"🚀 Starting video creation process for language '{language_code}'")
    
    # Dynamically load the configuration for the specified language
    try:
        Config = get_config(language_code)
        print(f"✅ Loaded configuration for language: {Config.CONTENT_LANGUAGE}")
    except ImportError as e:
        print(f"❌ {e}")
        sys.exit(1)

    keywords_to_process = []
    if keyword:
        keywords_to_process.append(keyword)
        print(f"✅ Processing a single keyword provided: '{keyword}'")
    else:
        # If no keyword is given, read from the channel-specific file or fallback to old method
        if channel_name:
            keywords_file_path = os.path.join("keywords", language_code, f"{channel_name}.txt")
            if os.path.exists(keywords_file_path):
                with open(keywords_file_path, 'r', encoding='utf-8') as f:
                    keywords_to_process = [line.strip() for line in f if line.strip()]
                if not keywords_to_process:
                    print(f"⚠️  The file '{keywords_file_path}' is empty. Nothing to process.")
                    sys.exit(0)
                print(f"Found {len(keywords_to_process)} keywords to process for channel '{channel_name}'.")
            else:
                print(f"❌ The keywords file '{keywords_file_path}' was not found.")
                sys.exit(1)
        else:
            # Fallback to old method
            keywords_file = f'keywords_{language_code}.txt'
            print(f"✅ No keyword or channel provided. Attempting to read from '{keywords_file}'...")
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    keywords_to_process = [line.strip() for line in f if line.strip()]
                if not keywords_to_process:
                    print(f"⚠️  The file '{keywords_file}' is empty. Nothing to process.")
                    sys.exit(0)
                print(f"Found {len(keywords_to_process)} keywords to process.")
            else:
                print(f"❌ The keywords file '{keywords_file}' was not found.")
                sys.exit(1)
            
    # Process all selected keywords
    for kw in keywords_to_process:
        run_pipeline_for_keyword(language_code, kw, Config, channel_name)

    print(f"\n\n{'='*60}")
    print("✅ All keywords have been processed.")
    print(f"{'='*60}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the complete video creation pipeline for a specific language.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    parser.add_argument('--keyword', type=str, default=None, help="(Optional) Single keyword to process. If omitted, all keywords from channel-specific or language file will be processed.")
    parser.add_argument('--channel', type=str, default=None, help="(Optional) Channel name to load keywords from keywords/{language}/{channel}.txt")
    
    args = parser.parse_args()
    main(args.language, args.keyword, args.channel) 