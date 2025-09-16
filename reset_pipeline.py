import os
import shutil
import glob

def reset_pipeline_state(language, channel_name=None):
    """Reset the pipeline state to start fresh."""
    print(f"Resetting pipeline state for language: {language}")
    if channel_name:
        print(f"Channel: {channel_name}")
    
    # 1. Remove the done tracking file(s)
    if channel_name:
        # Remove channel-specific done file
        done_file = f"keywords/done/keywords_{language}_{channel_name}_done.txt"
        if os.path.exists(done_file):
            os.remove(done_file)
            print(f"✓ Removed channel tracking file: {done_file}")
    else:
        # Remove all done files for the language (old and new format)
        old_done_file = f"keywords/done/keywords_{language}_done.txt"
        if os.path.exists(old_done_file):
            os.remove(old_done_file)
            print(f"✓ Removed old tracking file: {old_done_file}")
        
        # Remove all channel-specific done files for this language
        done_pattern = f"keywords/done/keywords_{language}_*_done.txt"
        for done_file in glob.glob(done_pattern):
            os.remove(done_file)
            print(f"✓ Removed channel tracking file: {done_file}")
    
    # 2. Clean up output directory
    output_dir = "output"
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✓ Removed: {file_path}")
            except Exception as e:
                print(f"✗ Could not remove {file_path}: {e}")
    
    # 3. Clean up audio directory
    audio_dir = "audio"
    if os.path.exists(audio_dir):
        for file in glob.glob(os.path.join(audio_dir, "*.mp3")):
            try:
                os.remove(file)
                print(f"✓ Removed audio: {file}")
            except Exception as e:
                print(f"✗ Could not remove {file}: {e}")
    
    # 4. Clean up any temp directories
    temp_dirs = ["temp", "tmp"]
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"✓ Removed temp directory: {temp_dir}")
            except Exception as e:
                print(f"✗ Could not remove {temp_dir}: {e}")
    
    print("\n" + "="*50)
    print("RESET COMPLETE!")
    if channel_name:
        print(f"The pipeline for channel '{channel_name}' will now start fresh from the first keyword.")
    else:
        print("The pipeline will now start fresh from the first keyword.")
    print("="*50)

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Reset pipeline state for a language and optionally a specific channel.")
    parser.add_argument('language', type=str, help="The language code (e.g., 'de', 'fr').")
    parser.add_argument('--channel', type=str, default=None, help="(Optional) Channel name to reset only that channel's progress.")
    
    args = parser.parse_args()
    reset_pipeline_state(args.language, args.channel) 