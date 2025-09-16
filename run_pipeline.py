import os
import subprocess
import time
import gc
import shutil
import sys
from datetime import datetime, timedelta
from config import get_config
import re

# Fix Windows console encoding issues
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows console
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Fallback: Replace problematic Unicode characters
        pass

def get_last_completed_step(done_file, keyword):
    """Checks the done file for the last successfully completed step for a keyword."""
    if not os.path.exists(done_file):
        return None
    with open(done_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith(keyword + ':'):
                return line.strip().split(':')[1]
    return None

def mark_step_as_done(done_file, keyword, step):
    """Marks a specific step as completed for a keyword."""
    # Read the whole file
    lines = []
    keyword_found = False
    if os.path.exists(done_file):
        with open(done_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    # Update the line for the keyword if it exists
    with open(done_file, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith(keyword + ':'):
                f.write(f"{keyword}:{step}\n")
                keyword_found = True
            else:
                f.write(line)
        # If the keyword wasn't in the file, add it
        if not keyword_found:
            f.write(f"{keyword}:{step}\n")

def cleanup_project_files(output_dir, audio_dir, videos_dir):
    """Permanently deletes the entire output, audio, and videos directories after a successful upload."""
    print(f"\n🧹 Cleaning up all generated files and directories...")
    
    # Force garbage collection to release file handles
    gc.collect()
    time.sleep(1)  # Give Windows time to release handles

    def force_delete_directory(dir_path):
        """Force delete a directory with multiple attempts and Windows-specific handling."""
        if not os.path.isdir(dir_path):
            return True
            
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # First attempt: standard deletion
                shutil.rmtree(dir_path)
                print(f"   - ✅ Permanently deleted directory: {dir_path}")
                return True
                
            except OSError as e:
                if attempt < max_attempts - 1:
                    print(f"   - 🔄 Attempt {attempt + 1} failed, retrying... ({e})")
                    
                    # Force close any remaining handles
                    gc.collect()
                    time.sleep(2)
                    
                    # Try Windows-specific force delete
                    if sys.platform == "win32":
                        try:
                            # Use Windows rmdir with force
                            subprocess.run(['rmdir', '/S', '/Q', dir_path], 
                                         shell=True, check=False, capture_output=True)
                            if not os.path.exists(dir_path):
                                print(f"   - ✅ Force deleted directory: {dir_path}")
                                return True
                        except:
                            pass
                else:
                    print(f"   - ❌ Failed to delete directory {dir_path} after {max_attempts} attempts: {e}")
                    return False
        return False

    # Delete directories with enhanced cleanup
    force_delete_directory(output_dir)
    force_delete_directory(audio_dir) 
    force_delete_directory(videos_dir)


def get_last_scheduled_time(channel_name, language, base_date=None):
    """
    Get the last scheduled video time for this channel by checking done files.
    Returns the next available time slot.
    
    Args:
        channel_name: Name of the channel
        language: Language code
        base_date: Optional base date for first video (defaults to Sept 13, 2025 based on your last scheduled)
    """
    done_file = f"keywords/done/keywords_{language}_{channel_name}_done.txt"
    
    if not os.path.exists(done_file):
        print(f"No previous videos found for channel '{channel_name}'. Starting from now.")
        return datetime.now()
    
    # Use your mentioned date as default base date
    if base_date is None:
        base_date = datetime(2025, 9, 11, 12, 0)  # Sept 11, 2025 at 12:00 (your last video date)
    
    video_count = 0
    
    try:
        with open(done_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'step5_upload' in line:
                    video_count += 1
        
        if video_count > 0:
            # Calculate last scheduled time: start from base date + (count * 12 hours)
            last_scheduled = base_date + timedelta(hours=12 * (video_count - 1))
            next_slot = last_scheduled + timedelta(hours=12)
            
            print(f"📊 Scheduling Analysis for '{channel_name}':")
            print(f"   - Found {video_count} completed videos")
            print(f"   - Base date: {base_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   - Last video was scheduled for: {last_scheduled.strftime('%Y-%m-%d %H:%M')}")
            print(f"   - Next video will be scheduled for: {next_slot.strftime('%Y-%m-%d %H:%M')}")
            
            # Ensure we don't schedule in the past, but maintain daily schedule
            if next_slot < datetime.now():
                print(f"   ⚠️  Calculated time is in the past. Finding next available daily slot.")
                # Find the next day at the same time (12:00)
                today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
                if today <= datetime.now():
                    # If 12:00 today has passed, schedule for tomorrow at 12:00
                    next_slot = today + timedelta(days=1)
                else:
                    # If 12:00 today hasn't passed, schedule for today at 12:00
                    next_slot = today
                print(f"   - Adjusted next slot to maintain daily schedule: {next_slot.strftime('%Y-%m-%d %H:%M')}")
            
            return next_slot
        else:
            print(f"No completed uploads found for channel '{channel_name}'. Starting from now.")
            return datetime.now()
            
    except Exception as e:
        print(f"Warning: Could not read done file {done_file}. Error: {e}")
        print("Starting from current time.")
        return datetime.now()


def get_last_scheduled_time_advanced(channel_name, language):
    """
    Advanced version: Parse actual scheduled times from log files or YouTube API.
    This would be more accurate but requires more setup.
    """
    # TODO: Implement if needed - could parse upload logs or query YouTube API
    # to get actual scheduled times of existing videos
    pass


def run_pipeline(language, channel_name, start_date_str=None, base_date_str=None, max_videos=None):
    """
    Orchestrates the entire video pipeline with step-by-step recovery and cleanup.
    """
    # 1. Setup - NEW: Load keywords from channel-specific file
    keyword_file_path = os.path.join("keywords", language, f"{channel_name}.txt")
    done_keyword_file = f"keywords/done/keywords_{language}_{channel_name}_done.txt"
    
    if not os.path.exists(keyword_file_path):
        print(f"❌ ERROR: Keyword file not found for channel '{channel_name}' in language '{language}'.")
        print(f"   Expected to find: {keyword_file_path}")
        print(f"   Please create the file with keywords for this channel.")
        return
    
    with open(keyword_file_path, 'r', encoding='utf-8') as f:
        # --- MODIFIED: Read keywords into a list to preserve file order ---
        all_keywords = [line.strip() for line in f if line.strip()]
    
    # --- NEW: Limit keywords if max_videos is specified ---
    if max_videos and max_videos > 0:
        # Filter out already completed keywords first
        pending_keywords = []
        for keyword in all_keywords:
            last_step = get_last_completed_step(done_keyword_file, keyword)
            if last_step != 'step5_upload':
                pending_keywords.append(keyword)
        
        # Limit to max_videos
        keywords_to_process = pending_keywords[:max_videos]
        print(f"📊 LIMIT APPLIED: Processing {len(keywords_to_process)} out of {len(pending_keywords)} pending keywords (max: {max_videos})")
    else:
        keywords_to_process = all_keywords
        print(f"Processing {len(keywords_to_process)} total keywords for channel '{channel_name}' in language '{language}'.")

    # 2. Scheduling & Credential Rotation - NEW: Continue from last scheduled video
    if start_date_str:
        start_datetime = datetime.strptime(start_date_str, '%Y-%m-%d')
        print(f"Using provided start date: {start_datetime.strftime('%Y-%m-%d %H:%M')}")
    else:
        # Parse base date if provided
        base_date = None
        if base_date_str:
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            print(f"Using custom base date: {base_date.strftime('%Y-%m-%d %H:%M')}")
        
        start_datetime = get_last_scheduled_time(channel_name, language, base_date)
        print(f"Continuing schedule from last video: {start_datetime.strftime('%Y-%m-%d %H:%M')}")
    
    # --- MODIFIED: Directly map channel_name to a specific credential file ---
    secrets_file_path = os.path.join('credentials', f"{channel_name}.json")

    if not os.path.exists(secrets_file_path):
        print(f"❌ ERROR: Credential file not found for channel '{channel_name}'.")
        print(f"   Expected to find: {secrets_file_path}")
        print(f"   Please make sure your client secret JSON is named '{channel_name}.json'")
        return
    
    print(f"Found credential set for '{channel_name}': {os.path.basename(secrets_file_path)}")
    
    Config = get_config(language)
    gemini_api_keys = [k for k in getattr(Config, 'GEMINI_API_KEYS', []) if k and "YOUR" not in k]
    num_gemini_keys = len(gemini_api_keys)
    if num_gemini_keys > 0:
        print(f"Found {num_gemini_keys} Gemini API keys.")
    
    videos_scheduled_count = 0
    
    # --- NEW: Smart credential tracking - only switch when quota exceeded ---
    current_credential_index = 0  # Start with first credential (client1.json)
    
    # 3. Process Each Keyword
    for i, keyword in enumerate(keywords_to_process):
        print("\n" + "="*60)
        print(f"Starting keyword {i+1}/{len(keywords_to_process)}: '{keyword}'")
        
        # --- FIXED: Ensure a clean slate before processing each keyword ---
        print("\n🧹 Wiping previous run data to ensure a clean state...")
        cleanup_project_files(Config.OUTPUT_DIR, Config.AUDIO_DIR, Config.VIDEOS_DIR)
        
        last_step = get_last_completed_step(done_keyword_file, keyword)
        if last_step == 'step5_upload':
            print("SUCCESS: This keyword has already been fully processed and uploaded. Skipping.")
            videos_scheduled_count += 1
            continue

        try:
            # --- Step 1 & 2: Content ---
            if not last_step:
                print("\n[1-2/5] Running Scraper & Content Generation...")
                # (Gemini Key Rotation Logic)
                # --- FIXED: Pass the current keyword and channel to step2_content.py ---
                step2_cmd = ['python', 'step2_content.py', language, '--keyword', keyword, '--channel', channel_name]
                if num_gemini_keys > 0:
                    gemini_key_index = (videos_scheduled_count // 5) % num_gemini_keys
                    selected_gemini_key = gemini_api_keys[gemini_key_index]
                    step2_cmd.extend(['--api-key', selected_gemini_key])
                    print(f"   Using Gemini API Key #{gemini_key_index + 1}")
                
                # --- FIXED: Allow real-time output from scraper ---
                print(f"   Running scraper for keyword: '{keyword}'...")
                try:
                    scraper_result = subprocess.run(['python', 'step1_scraper.py', language, keyword], 
                                                   check=False, encoding='utf-8', errors='replace')
                    
                    # Check if scraper failed due to insufficient products
                    if scraper_result.returncode == 10:
                        print(f"🟡 WARNING: Not enough products with videos found for '{keyword}'. Skipping to next keyword.")
                        continue  # Skip to next keyword in the loop
                    elif scraper_result.returncode != 0:
                        # Other scraper errors should still stop the pipeline
                        print(f"❌ Scraper failed with return code {scraper_result.returncode}")
                        raise subprocess.CalledProcessError(scraper_result.returncode, scraper_result.args)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Scraper subprocess failed: {e}")
                    raise e
                
                subprocess.run(step2_cmd, check=True, encoding='utf-8', errors='replace')
                mark_step_as_done(done_keyword_file, keyword, 'step2_content')
            else:
                print("\n[1-2/5] Skipping Scraper & Content (already done).")

            # --- Step 3: Video ---
            if last_step in [None, 'step2_content']:
                print("\n[3/5] Running Video Assembly...")
                subprocess.run(['python', 'step3_video_simple.py', language], check=True, encoding='utf-8', errors='replace')
                mark_step_as_done(done_keyword_file, keyword, 'step3_video')
            else:
                print("\n[3/5] Skipping Video Assembly (already done).")

            # --- Step 4: Thumbnail ---
            if last_step in [None, 'step2_content', 'step3_video']:
                print("\n[4/5] Running Thumbnail Generation...")
                subprocess.run(['python', 'step4_thumbnail.py', language], check=True, encoding='utf-8', errors='replace')
                mark_step_as_done(done_keyword_file, keyword, 'step4_thumbnail')
            else:
                print("\n[4/5] Skipping Thumbnail Generation (already done).")
            
            # --- Step 5: Upload (with smart credential management) ---
            upload_successful = False
            
            # --- MODIFIED: Use the directly mapped credential file, removing rotation ---
            # The loop for rotating through credentials has been removed to directly use the channel's specific file.
            
            selected_secrets_file = secrets_file_path
            client_name = channel_name  # Use channel name directly instead of "client_channelname"
            # The token file is now directly associated with the channel name.
            token_path = os.path.join('tokens', f"token_{client_name}.pickle")
            
            print(f"\n[5/5] Attempting upload with credential for channel '{channel_name}'...")
            
            # --- MODIFIED: Scheduling logic continues from last scheduled video ---
            # Since start_datetime is already the next available slot, we just add 12 hours for each new video
            publish_datetime = start_datetime + timedelta(hours=12 * videos_scheduled_count)
            publish_at_iso = publish_datetime.isoformat() + "Z"
            
            upload_cmd = [
                'python', 'step5_youtube_uploader.py', language,
                '--channel', channel_name,
                '--publish-at', publish_at_iso,
                '--secrets-path', selected_secrets_file,
                '--token-path', token_path
            ]
            
            try:
                # --- FIXED: Don't capture output during authentication - show in real-time ---
                result = subprocess.run(upload_cmd, check=True, text=True, encoding='utf-8', errors='replace')
                upload_successful = True
            except subprocess.CalledProcessError as e:
                # (Error handling logic without credential rotation)
                print(f"   WARNING: Upload failed for channel '{channel_name}'.")
                print(f"   Return code: {e.returncode}")
                
                # Try to determine error type from return code or other indicators
                if e.returncode == 1:
                    print("   ERROR: Upload process failed. This could be due to:")
                    print("   - Authentication issues")
                    print("   - API quota exceeded") 
                    print("   - Network connectivity issues")
                    print("   - File not found")
                    
                print("   ERROR: An unrecoverable error occurred during upload. Stopping.")
                raise e # Re-raise the exception to stop the pipeline
            
            if upload_successful:
                mark_step_as_done(done_keyword_file, keyword, 'step5_upload')
                videos_scheduled_count += 1
                print(f"\nSUCCESS: Successfully processed and scheduled video for keyword: '{keyword}'")
                
                # --- Cleanup is now handled at the start of the next loop ---
                
            else:
                print(f"\nERROR: All credential sets failed for keyword '{keyword}'. Moving to next keyword.")
                continue  # Continue to next keyword instead of stopping

        except (subprocess.CalledProcessError, Exception) as e:
            print(f"\n❌ FATAL ERROR: An unrecoverable error occurred while processing keyword '{keyword}'.")
            if isinstance(e, subprocess.CalledProcessError):
                # This will catch the re-raised exception from the uploader
                print(f"   - The pipeline failed at the upload step.")
            else:
                print(f"   - Error details: {e}")
            print("   - The pipeline will now stop. Please fix the issue and restart the script.")
            print("   - The pipeline will attempt to resume from the last completed step for this keyword.")
            break  # Stop the main keyword loop and exit the script gracefully

def process_keyword(args):
    """Function to process a single keyword, designed to be run in a thread."""
    i, keyword, language, channel_name, start_datetime, done_keyword_file, secrets_file_path, gemini_api_keys, videos_scheduled_count = args
    
    Config = get_config(language)
    num_gemini_keys = len(gemini_api_keys)

    # --- NEW: Create a unique directory for this thread to work in ---
    session_id = f"{keyword.replace(' ', '_')}_{os.urandom(4).hex()}"
    base_output_dir = os.path.join(Config.OUTPUT_DIR, session_id)
    
    # Create unique paths for this session
    session_output_dir = os.path.join(base_output_dir, "output")
    session_audio_dir = os.path.join(base_output_dir, "audio")
    session_videos_dir = os.path.join(base_output_dir, "videos")
    
    # Ensure these directories exist
    os.makedirs(session_output_dir, exist_ok=True)
    os.makedirs(session_audio_dir, exist_ok=True)
    os.makedirs(session_videos_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print(f"Thread for '{keyword}' using session directory: {session_id}")


    # Now, we need to pass these unique directories to each script.
    # This requires modifying the subprocess calls.
    common_args = [
        '--output-dir', session_output_dir,
        '--audio-dir', session_audio_dir,
        '--videos-dir', session_videos_dir
    ]

    last_step = get_last_completed_step(done_keyword_file, keyword)
    if last_step == 'step5_upload':
        print(f"SUCCESS: Keyword '{keyword}' has already been fully processed. Skipping.")
        shutil.rmtree(base_output_dir) # Clean up session directory
        return True # Indicate success

    try:
        # --- Step 1: Scraper ---
        if not last_step:
            print(f"\n[1/5] Running Scraper for '{keyword}'...")
            scraper_cmd = ['python', 'step1_scraper.py', language, keyword] + common_args
            try:
                scraper_result = subprocess.run(scraper_cmd, check=False, encoding='utf-8', errors='replace')
                if scraper_result.returncode == 10:
                    print(f"🟡 WARNING: Not enough products for '{keyword}'. Skipping.")
                    shutil.rmtree(base_output_dir)
                    return None # Indicate skip
                elif scraper_result.returncode != 0:
                    print(f"❌ Scraper failed for '{keyword}' with return code {scraper_result.returncode}")
                    raise subprocess.CalledProcessError(scraper_result.returncode, scraper_result.args)
            except subprocess.CalledProcessError as e:
                print(f"❌ Scraper subprocess failed for '{keyword}': {e}")
                raise e

        # --- Step 2: Content Generation (No longer locked) ---
        if not last_step:
            print(f"\n[2/5] Running Content Generation for '{keyword}'...")
            step2_cmd = ['python', 'step2_content.py', language, '--keyword', keyword, '--channel', channel_name] + common_args
            if num_gemini_keys > 0:
                gemini_key_index = (videos_scheduled_count // 5) % num_gemini_keys
                selected_gemini_key = gemini_api_keys[gemini_key_index]
                step2_cmd.extend(['--api-key', selected_gemini_key])
            subprocess.run(step2_cmd, check=True, encoding='utf-8', errors='replace')
            mark_step_as_done(done_keyword_file, keyword, 'step2_content')
        else:
            print(f"\n[1-2/5] Skipping Scraper & Content for '{keyword}' (already done).")

        # --- Step 3: Video ---
        if last_step in [None, 'step2_content']:
            print(f"\n[3/5] Running Video Assembly for '{keyword}'...")
            step3_cmd = ['python', 'step3_video_simple.py', language] + common_args
            subprocess.run(step3_cmd, check=True, encoding='utf-8', errors='replace')
            mark_step_as_done(done_keyword_file, keyword, 'step3_video')
        else:
            print(f"\n[3/5] Skipping Video Assembly for '{keyword}' (already done).")

        # --- Step 4: Thumbnail (Locked) ---
        if last_step in [None, 'step2_content', 'step3_video']:
            print(f"\n[4/5] Running Thumbnail Generation for '{keyword}'...")
            step4_cmd = ['python', 'step4_thumbnail.py', language] + common_args
            subprocess.run(step4_cmd, check=True, encoding='utf-8', errors='replace')
            mark_step_as_done(done_keyword_file, keyword, 'step4_thumbnail')
        else:
            print(f"\n[4/5] Skipping Thumbnail Generation for '{keyword}' (already done).")
        
        # --- Step 5: Upload ---
        token_path = os.path.join('tokens', f"token_{channel_name}.pickle")
        publish_datetime = start_datetime + timedelta(hours=12 * videos_scheduled_count)
        publish_at_iso = publish_datetime.isoformat() + "Z"
        
        upload_cmd = [
            'python', 'step5_youtube_uploader.py', language,
            '--channel', channel_name,
            '--publish-at', publish_at_iso,
            '--secrets-path', secrets_file_path,
            '--token-path', token_path
        ] + common_args
        
        print(f"\n[5/5] Attempting upload for '{keyword}'...")
        result = subprocess.run(upload_cmd, check=True, text=True, encoding='utf-8', errors='replace')
        
        mark_step_as_done(done_keyword_file, keyword, 'step5_upload')
        print(f"\nSUCCESS: Successfully processed and scheduled video for keyword: '{keyword}'")
        
        # Clean up the session directory after a successful upload
        print(f"🧹 Cleaning up session directory: {session_id}")
        shutil.rmtree(base_output_dir)

        return True

    except (subprocess.CalledProcessError, Exception) as e:
        print(f"\n❌ FATAL ERROR processing keyword '{keyword}': {e}")
        # Clean up the session directory on failure as well
        if os.path.exists(base_output_dir):
            shutil.rmtree(base_output_dir)
        return False


if __name__ == "__main__":
    import argparse
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    parser = argparse.ArgumentParser(description="Run the full AutoVideo pipeline with smart scheduling and concurrency.")
    parser.add_argument('language', type=str, help="Language code (e.g., 'es').")
    parser.add_argument('channel_name', type=str, help="Unique name for the YouTube channel.")
    parser.add_argument('--start-date', type=str, help="Optional start date for scheduling (YYYY-MM-DD). Overrides automatic continuation.")
    parser.add_argument('--base-date', type=str, help="Base date for first video calculation (YYYY-MM-DD).")
    parser.add_argument('--max-videos', type=int, help="Maximum number of videos to create.")
    parser.add_argument('--num-workers', type=int, default=1, help="Number of videos to process concurrently.")
    parser.add_argument('--reset', action='store_true', help="Reset the pipeline by deleting output, done files, and tokens.")
    args = parser.parse_args()
    
    # --- NEW: Handle the --reset flag ---
    if args.reset:
        print("💥 --reset flag detected. Resetting the pipeline...")
        
        # 1. Delete the entire output directory
        output_dir = "output"
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
                print(f"  - ✅ Deleted directory: {output_dir}")
            except Exception as e:
                print(f"  - ⚠️  Could not delete {output_dir}: {e}")
        os.makedirs(output_dir, exist_ok=True) # Recreate it
        
        # 2. Delete all done files
        done_files_path = os.path.join("keywords", "done")
        if os.path.exists(done_files_path):
            for item in os.listdir(done_files_path):
                if item.endswith("_done.txt"):
                    try:
                        os.remove(os.path.join(done_files_path, item))
                        print(f"  - ✅ Deleted done file: {item}")
                    except Exception as e:
                        print(f"  - ⚠️  Could not delete {item}: {e}")

        # 3. Delete the tokens directory
        tokens_dir = "tokens"
        if os.path.exists(tokens_dir):
            try:
                shutil.rmtree(tokens_dir)
                print(f"  - ✅ Deleted directory: {tokens_dir}")
            except Exception as e:
                print(f"  - ⚠️  Could not delete {tokens_dir}: {e}")
        os.makedirs(tokens_dir, exist_ok=True) # Recreate it

        print("✅ Pipeline reset complete. Starting a fresh run.")
        print("="*60)


    # We need to call the original setup logic from run_pipeline
    # This is a bit of a hack; ideally, we'd refactor run_pipeline into setup and execution parts.
    
    # 1. Setup from run_pipeline
    keyword_file_path = os.path.join("keywords", args.language, f"{args.channel_name}.txt")
    done_keyword_file = f"keywords/done/keywords_{args.language}_{args.channel_name}_done.txt"
    
    if not os.path.exists(keyword_file_path):
        print(f"❌ ERROR: Keyword file not found: {keyword_file_path}")
        sys.exit(1)
        
    with open(keyword_file_path, 'r', encoding='utf-8') as f:
        all_keywords = [line.strip() for line in f if line.strip()]
    
    pending_keywords = []
    if args.max_videos and args.max_videos > 0:
        for keyword in all_keywords:
            if get_last_completed_step(done_keyword_file, keyword) != 'step5_upload':
                pending_keywords.append(keyword)
        keywords_to_process = pending_keywords[:args.max_videos]
        print(f"📊 LIMIT APPLIED: Processing {len(keywords_to_process)} of {len(pending_keywords)} pending keywords.")
    else:
        keywords_to_process = all_keywords
        print(f"Processing {len(keywords_to_process)} total keywords for channel '{args.channel_name}'.")

    if args.start_date:
        start_datetime = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        base_date = datetime.strptime(args.base_date, '%Y-%m-%d') if args.base_date else None
        start_datetime = get_last_scheduled_time(args.channel_name, args.language, base_date)

    secrets_file_path = os.path.join('credentials', f"{args.channel_name}.json")
    if not os.path.exists(secrets_file_path):
        print(f"❌ ERROR: Credential file not found: {secrets_file_path}")
        sys.exit(1)
        
    Config = get_config(args.language)
    gemini_api_keys = [k for k in getattr(Config, 'GEMINI_API_KEYS', []) if k and "YOUR" not in k]
    
    # 2. Concurrent Execution
    videos_scheduled_count = 0
    
    tasks = []
    for i, keyword in enumerate(keywords_to_process):
        # We need to figure out the correct scheduled count for each video's publish time
        # This is tricky as we don't know the order of completion.
        # For now, let's just increment. A better solution would be to use a shared counter.
        task_args = (i, keyword, args.language, args.channel_name, start_datetime, done_keyword_file, secrets_file_path, gemini_api_keys, videos_scheduled_count + i)
        tasks.append(task_args)

    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        futures = {executor.submit(process_keyword, task): task for task in tasks}
        
        for future in as_completed(futures):
            keyword = futures[future][1] # Get keyword from original task args
            try:
                result = future.result()
                if result is True:
                    print(f"✅ COMPLETED: Keyword '{keyword}' processed successfully.")
                elif result is None:
                    print(f"⏩ SKIPPED: Keyword '{keyword}' was skipped.")
                else:
                    print(f"⚠️ FAILED: Keyword '{keyword}' failed processing.")
            except Exception as exc:
                print(f"💥 EXCEPTION: An error occurred processing keyword '{keyword}': {exc}")
    
    print("\n\nPipeline finished.")
    # run_pipeline(args.language, args.channel_name, args.start_date, args.base_date, args.max_videos) 