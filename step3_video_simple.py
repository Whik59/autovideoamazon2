"""
Step 3: Super Simple & Fast Video Assembly
Just concatenate videos with audio - no complex overlays
"""

import os
import json
import subprocess
import time
import re
from html2image import Html2Image
from pathlib import Path

class SimpleVideoAssembler:
    """
    Ultra-simple video assembler focused on speed.
    No complex overlays, just fast concatenation.
    """
    
    def __init__(self, config):
        self.config = config
        # --- MODIFIED: Create a temp directory inside the session-specific output directory ---
        self.temp_dir = os.path.join(self.config.OUTPUT_DIR, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.hti = Html2Image(output_path=self.temp_dir, size=(1920, 1080))
        
    def run(self):
        """Main entry point - super fast approach."""
        print("🚀 STEP 3: Super Fast Video Assembly")
        print("=" * 40)
        start_time = time.time()
        
        try:
            data = self._load_data()
            if not data: 
                return
                
            keyword = data.get('keyword', 'product')
            products = sorted(data.get('products', []), key=lambda p: p.get('position', 999), reverse=True)
            
            # Step 1: Generate the intro overlay image
            print("\n🖼️ Generating intro overlay image...")
            intro_overlay_path = self._create_intro_overlay_image(keyword, products)

            print(f"📦 Processing {len(products)} products...")
            
            # Step 2: Generate overlay images for each product
            print("\n🖼️ Generating product overlay images...")
            product_overlays = self._generate_product_overlay_images(products)
            if not product_overlays:
                print("❌ Failed to generate overlays. Aborting.")
                return

            # Step 3: Create a video segment for each product with overlays burned in
            # Pass the intro overlay path to be applied to the first segment
            final_segments = self._create_segments_with_timed_overlays(products, product_overlays, intro_overlay_path)
            if not final_segments:
                print("❌ No video segments created.")
                return
            
            # Step 4: Fast concatenation and final audio mix
            sanitized_keyword = self._sanitize_filename(keyword)
            output_path = os.path.join(self.config.OUTPUT_DIR, f"{sanitized_keyword}_final_video.mp4")
            success = self._fast_concatenate_and_add_music(final_segments, output_path)
            
            # --- NEW: Save the updated data with durations ---
            if success:
                self._save_updated_data(data)
            # --- END ---

            if success:
                end_time = time.time()
                print(f"\n✅ Video completed in {end_time - start_time:.2f} seconds!")
                print(f"📁 Output: {output_path}")
            else:
                print("❌ Failed to create final video.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self._cleanup()
    
    def _create_intro_overlay_image(self, keyword, products):
        """Generates a single PNG image for the intro overlay."""
        intro_html_path = 'intro_template.html'
        intro_css_path = 'intro_style.css'
        
        if not os.path.exists(intro_html_path) or not os.path.exists(intro_css_path):
            print("  ❌ Intro template files (HTML/CSS) not found.")
            return None
            
        with open(intro_html_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        html_content = html_template.replace('{{ keyword }}', keyword.upper())

        for i in range(1, 4):
            product = next((p for p in products if p.get('position') == i), None)
            image_path = ""
            if product:
                image_path = next((fp for ft, fp in product.get('downloaded_files', []) if ft == 'image'), "")
            
            # --- THE FIX: Convert path to a file URI for reliability ---
            image_uri = ""
            if image_path and os.path.exists(image_path):
                # First, get the absolute path. THEN, convert to URI.
                abs_path = os.path.abspath(image_path)
                image_uri = Path(abs_path).as_uri()

            html_content = html_content.replace(f"{{{{ image_{i} }}}}", image_uri)

        try:
            intro_image_path = self.hti.screenshot(
                html_str=html_content, 
                css_file=intro_css_path, 
                save_as="intro_overlay.png"
            )[0]
            print("  ✅ Intro overlay image created successfully.")
            return intro_image_path
        except Exception as e:
            print(f"  ❌ An error occurred during intro overlay generation: {e}")
            return None

    def _sanitize_filename(self, text):
        """Removes special characters to create a safe filename."""
        # Normalize to handle accents
        import unicodedata
        import re
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        # Replace spaces and remove unsafe characters
        text = re.sub(r'[^a-zA-Z0-9_.\-]', '_', text)
        return text

    def _generate_product_overlay_images(self, products):
        """
        Generates three separate overlay images for each product: title, price,
        and a call-to-action (CTA) for independent timing control.
        """
        # Renamed from _generate_overlay_images to be more specific
        overlays = []
        overlay_html_path = 'overlay_template.html'
        overlay_css_path = 'overlay_style.css'
        
        if not os.path.exists(overlay_html_path) or not os.path.exists(overlay_css_path):
            print("  ❌ Overlay template files (HTML/CSS) not found.")
            return None
            
        with open(overlay_html_path, 'r', encoding='utf-8') as f: html_template = f.read()
        with open(overlay_css_path, 'r', encoding='utf-8') as f: base_css = f.read()

        for product in products:
            try:
                pos = product.get('position', 'NA')
                short_title = product.get('short_title', 'Product Title')
                price = product.get('price', '')
                rating = product.get('rating', 0)

                # --- NEW: Calculate rating percentage for dynamic stars ---
                try:
                    rating_float = float(str(rating).replace(',', '.'))
                except (ValueError, TypeError):
                    rating_float = 0.0
                
                # Ensure percentage is between 0 and 100
                rating_percentage = max(0, min(100, (rating_float / 5.0) * 100))

                html_content = (
                    html_template
                    .replace('{{ position }}', str(pos))
                    .replace('{{ short_title }}', short_title)
                    .replace('{{ price }}', price)
                    .replace('{{ rating_percentage }}', f"{rating_percentage:.2f}")
                    .replace('{{ rating }}', str(rating))
                    .replace('{{ info_banner_text }}', self.config.OVERLAY_INFO_BANNER_TEXT)
                    .replace('{{ cta_banner_text }}', self.config.OVERLAY_CTA_BANNER_TEXT)
                )
                
                # --- Create Title Overlay (Top Left) ---
                css_title = base_css + " .price-container, .cta-group { visibility: hidden; } "
                title_overlay_path = self.hti.screenshot(
                    html_str=html_content, css_str=css_title, save_as=f"title_overlay_{pos}.png"
                )[0]
                
                # --- Create Price Overlay (Top Right) ---
                css_price = base_css + " .title-container, .cta-group { visibility: hidden; } "
                price_overlay_path = self.hti.screenshot(
                    html_str=html_content, css_str=css_price, save_as=f"price_overlay_{pos}.png"
                )[0]

                # --- Create CTA Overlay (Bottom Center) ---
                css_cta = base_css + " .title-container, .price-container { visibility: hidden; } "
                cta_overlay_path = self.hti.screenshot(
                    html_str=html_content, css_str=css_cta, save_as=f"cta_overlay_{pos}.png"
                )[0]

                overlays.append({
                    'title_path': title_overlay_path,
                    'price_path': price_overlay_path,
                    'cta_path': cta_overlay_path,
                    'position': pos
                })
                print(f"  ✅ Generated overlays for product #{pos}")
            except Exception as e:
                print(f"  ❌ Failed to generate overlays for product #{pos}: {e}")
                return None
        
        return overlays
    
    def _load_data(self):
        """Load product data."""
        data_file = os.path.join(self.config.OUTPUT_DIR, "enhanced_product.json")
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            return None
            
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"✅ Loaded {len(data.get('products', []))} products")
        return data

    def _save_updated_data(self, data):
        """Saves the updated data with new fields like segment durations."""
        data_file = os.path.join(self.config.OUTPUT_DIR, "enhanced_product.json")
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("💾 Updated product data saved with segment durations.")
        except Exception as e:
            print(f"  ⚠️ Warning: Could not save updated product data. Error: {e}")

    def _concatenate_product_videos(self, video_files, product_position):
        """Concatenates multiple video files into a single file for a product."""
        output_path = os.path.join(self.temp_dir, f"concatenated_video_{product_position}.mp4")
        
        # Create a file list for ffmpeg
        list_file_path = os.path.join(self.temp_dir, f"video_list_{product_position}.txt")
        with open(list_file_path, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                f.write(f"file '{os.path.abspath(video_file)}'\n")

        # ffmpeg command to concatenate
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', 
            '-i', list_file_path, 
            '-c', 'copy', 
            output_path
        ]

        if not self._run_ffmpeg(cmd):
            print(f"     -> ❌ Failed to concatenate videos for product #{product_position}.")
            return None
            
        return output_path

    def _create_segments_with_timed_overlays(self, products, product_overlays, intro_overlay_path=None):
        """
        Creates video segments for each product, burning in the title and price
        overlays with specific timing delays. Also adds swoosh transitions.
        """
        segments = []
        swoosh_path = os.path.join("thumbnail", "swoosh_fixed.mp3")

        for i, product in enumerate(products):
            pos = product.get('position', 'NA')
            print(f"  🎬 Processing segment for product #{pos}...")

            audio_file = product.get('final_audio_file')
            if not audio_file or not os.path.exists(audio_file) or not audio_file.endswith('.wav'):
                print(f"     -> ERROR: Missing or invalid audio file for product #{pos}. Expected a .wav file. Skipping.")
                continue
            
            # --- MODIFIED: Handle multiple video files ---
            video_files = [fp for ft, fp in product.get('downloaded_files', []) if ft == 'video']

            if not video_files:
                print(f"     -> ERROR: No video files found for product #{pos}. Skipping.")
                continue

            # If there are multiple video clips, concatenate them first
            if len(video_files) > 1:
                print(f"     -> Found {len(video_files)} video clips. Concatenating them into a single file.")
                video_file = self._concatenate_product_videos(video_files, pos)
                if not video_file:
                    print(f"     -> ERROR: Failed to concatenate video clips for product #{pos}. Skipping.")
                    continue
            else:
                video_file = video_files[0]
            # --- END MODIFICATION ---

            if not audio_file or not video_file:
                print(f"     -> ERROR: Missing audio or final video file for product #{pos}. Skipping.")
                continue

            # Log video properties for debugging
            video_info = self._get_video_info(video_file)
            print(f"     -> Video info: {video_info} -> Will be normalized to 1920x1080 (16:9)")
            
            # Validate that the video file is actually processable
            if not self._validate_video_file(video_file):
                print(f"     -> ERROR: Video file for product #{pos} is corrupted or unreadable. Skipping.")
                continue

            audio_duration = self._get_media_duration(audio_file)
            if audio_duration is None:
                print(f"     -> ERROR: Could not get audio duration for product #{pos}. Skipping.")
                continue

            # --- NEW: Store duration in the product dictionary ---
            product['segment_duration'] = audio_duration
            # --- END ---

            # Create the initial raw segment (video looped to audio duration + audio)
            # IMPORTANT: Force video to 16:9 aspect ratio and normalize resolution
            raw_segment_path = os.path.join(self.temp_dir, f"raw_segment_{pos}.mp4")
            cmd_raw = [
                'ffmpeg', '-y', '-loglevel', 'error',
                '-stream_loop', '-1', '-i', video_file,
                '-i', audio_file,
                '-map', '0:v:0', '-map', '1:a:0',
                # Video processing: Force 16:9 aspect ratio with proper scaling and cropping
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-t', str(audio_duration),
                raw_segment_path
            ]
            if not self._run_ffmpeg(cmd_raw):
                print(f"     -> ❌ Failed to create raw segment for product #{pos}.")
                continue
            
            final_segment_path = os.path.join(self.temp_dir, f"final_segment_{pos}.mp4")
            overlay_info = product_overlays[i]

            # --- Build Inputs and Filter Complex Dynamically ---
            inputs = ['-i', raw_segment_path]
            filter_parts = []
            last_stream = "[0:v]"
            
            # Create a list of all overlays to be applied in this segment
            overlays_to_apply = []
            if i == 0 and intro_overlay_path:
                overlays_to_apply.append({
                    'path': intro_overlay_path,
                    'enable': 'between(t,0,5)',
                    'pos': 'x=(W-w)/2:y=(H-h)/2'
                })
            
            # --- MODIFIED: Title Overlay Timing to show at start and end ---
            price_start_time = audio_duration - 10
            cta_start_time = audio_duration - 5

            if i == 0:  # First product segment, which has the intro
                # Show for 5s after the intro, and for the last 5s.
                title_enable_str = f"between(t,5,10)+between(t,{audio_duration - 5},{audio_duration})"
            else:  # Subsequent product segments
                # Show for the first 5s (with a small delay), and for the last 5s.
                title_enable_str = f"between(t,0.5,5.5)+between(t,{audio_duration - 5},{audio_duration})"

            overlays_to_apply.extend([
                {'path': overlay_info['title_path'], 'enable': title_enable_str, 'pos': 'x=50:y=50'},
                {'path': overlay_info['price_path'], 'enable': f'between(t,{price_start_time},{audio_duration})', 'pos': 'x=W-w-50:y=50'},
                {'path': overlay_info['cta_path'], 'enable': f'between(t,{cta_start_time},{audio_duration})', 'pos': 'x=(W-w)/2:y=H-h-90'}
            ])

            # Build the inputs and filter chain from the list
            for idx, overlay in enumerate(overlays_to_apply):
                inputs.extend(['-i', overlay['path']])
                overlay_stream = f"[{idx + 1}:v]"
                output_tag = f"[v{idx + 1}]"
                
                # The very last overlay in the chain doesn't need an output tag
                if idx == len(overlays_to_apply) - 1:
                    output_tag = ""
                    
                filter_parts.append(
                    f"{last_stream}{overlay_stream}overlay={overlay['pos']}:enable='{overlay['enable']}'{output_tag}"
                )
                last_stream = output_tag

            filter_chain = ";".join(filter_parts)
            
            cmd_overlay = [
                'ffmpeg', '-y', '-loglevel', 'error',
                *inputs,
                '-filter_complex', filter_chain,
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '28',
                '-c:a', 'copy',
                final_segment_path
            ]
            
            if self._run_ffmpeg(cmd_overlay):
                print(f"     -> ✅ Segment with overlays created [Duration: {audio_duration:.2f}s]")
                segments.append(final_segment_path)

                if i < len(products) - 1 and os.path.exists(swoosh_path):
                    swoosh_segment_path = os.path.join(self.temp_dir, f"swoosh_{pos}.mp4")
                    swoosh_cmd = [
                        'ffmpeg', '-y', '-loglevel', 'error',
                        '-i', swoosh_path,
                        '-stream_loop', '-1', '-i', video_file,
                        '-map', '1:v:0', '-map', '0:a:0',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                        '-shortest',
                        swoosh_segment_path
                    ]
                    if self._run_ffmpeg(swoosh_cmd):
                        segments.append(swoosh_segment_path)
                        print(f"        -> Swoosh transition added.")
            else:
                print(f"     -> ❌ Failed to apply timed overlays.")

        total_duration = sum(self._get_media_duration(s) for s in segments)
        print(f"\n📊 Total calculated segment duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        return segments

    def _fast_concatenate_and_add_music(self, segments, output_path):
        """
        Super fast concatenation of pre-made segments using FFmpeg, then adds music.
        """
        if not segments:
            return False
            
        print(f"\n🔗 Concatenating {len(segments)} final segments...")
        
        concat_list = os.path.join(self.temp_dir, "concat_list.txt")
        with open(concat_list, 'w', encoding='utf-8') as f:
            for segment in segments:
                abs_path = os.path.abspath(segment).replace(os.sep, '/')
                f.write(f"file '{abs_path}'\n")
        
        concatenated_video_path = os.path.join(self.temp_dir, "concatenated.mp4")
        cmd_concat = [
            'ffmpeg', '-y', '-loglevel', 'warning',
            '-f', 'concat', '-safe', '0', '-i', concat_list,
            '-c', 'copy',
            concatenated_video_path
        ]
        
        if not self._run_ffmpeg(cmd_concat, timeout=180):
            print("   -> ❌ Failed to concatenate segments.")
            return False

        if os.path.exists(self.config.BACKGROUND_MUSIC_PATH):
            print("🎵 Adding background music...")
            cmd_music = [
                'ffmpeg', '-y', '-loglevel', 'warning',
                '-i', concatenated_video_path,
                '-i', self.config.BACKGROUND_MUSIC_PATH,
                '-filter_complex', f'[1:a]volume={self.config.BACKGROUND_MUSIC_VOLUME}[bg];[0:a][bg]amix=inputs=2:duration=first[audio]',
                '-map', '0:v', '-map', '[audio]',
                '-c:v', 'copy', 
                '-c:a', 'aac', 
                '-b:a', '128k',
                output_path
            ]
            return self._run_ffmpeg(cmd_music, timeout=180)
        else:
            import shutil
            shutil.move(concatenated_video_path, output_path)
            return True

    def _get_media_duration(self, file_path):
        """Gets the duration of a media file using ffprobe."""
        if not file_path or not os.path.exists(file_path):
            return 0
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 
            'format=duration', '-of', 
            'default=noprint_wrappers=1:nokey=1', file_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return float(result.stdout.strip())
        except Exception:
            return 0

    def _get_video_info(self, video_path):
        """Gets video resolution and aspect ratio for debugging."""
        if not video_path or not os.path.exists(video_path):
            return "Unknown"
        
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0', video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                width, height = map(int, result.stdout.strip().split('x'))
                aspect_ratio = width / height
                return f"{width}x{height} (ratio: {aspect_ratio:.2f})"
            return "Could not determine"
        except Exception:
            return "Error reading"

    def _validate_video_file(self, video_path):
        """Validates that a video file is readable and has basic video properties."""
        if not video_path or not os.path.exists(video_path):
            return False
        
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,width,height,duration',
            '-of', 'csv=p=0', video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                # If ffprobe can read the file and get video stream info, it's valid
                return True
            return False
        except Exception:
            return False

    def _get_product_video_path(self, product):
        """Get video file path for product."""
        for file_type, file_path in product.get('downloaded_files', []):
            if file_type == 'video' and os.path.exists(file_path):
                return file_path
        return None
    
    def _run_ffmpeg(self, cmd, timeout=60):
        """Run FFmpeg command with timeout."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode != 0:
                print(f"\n--- FFmpeg Error ---\n{result.stderr}\n--- End Error ---")
                return False
            return True
        except Exception as e:
            print(f"\n--- Python Error running FFmpeg ---\n{e}\n--- End Error ---")
            return False
    
    def _cleanup(self):
        """Clean up temp files."""
        if os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up: {self.temp_dir}")
            except:
                pass

if __name__ == "__main__":
    import sys
    import argparse
    from config import get_config

    parser = argparse.ArgumentParser(description="Standalone video assembler for a specific language.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    # --- NEW: Add arguments for session directories ---
    parser.add_argument('--output-dir', type=str, help="Override default output directory.")
    parser.add_argument('--audio-dir', type=str, help="Override default audio directory.")
    parser.add_argument('--videos-dir', type=str, help="Override default videos directory.")
    args = parser.parse_args()

    try:
        print(f"▶️  Running Step 3 in standalone mode for language '{args.language}'")
        Config = get_config(args.language)
        print(f"✅ Loaded configuration for language: {Config.CONTENT_LANGUAGE}")

        # --- NEW: Override config paths if provided ---
        if args.output_dir:
            Config.OUTPUT_DIR = args.output_dir
            print(f"   Overriding OUTPUT_DIR: {Config.OUTPUT_DIR}")
        if args.audio_dir:
            Config.AUDIO_DIR = args.audio_dir
            print(f"   Overriding AUDIO_DIR: {Config.AUDIO_DIR}")
        if args.videos_dir:
            Config.VIDEOS_DIR = args.videos_dir
            print(f"   Overriding VIDEOS_DIR: {Config.VIDEOS_DIR}")

        assembler = SimpleVideoAssembler(Config)
        assembler.run()

    except ImportError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)
