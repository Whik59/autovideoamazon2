import os
import time
import hashlib
import json
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# The API key is passed directly to the client
API_KEY = "AIzaSyAz-2QpjTB17-iJNVGZm1DRVO6HUmxV6rg"

# Cache directory for generated images
CACHE_DIR = "output/cache"

def get_prompt_hash(prompt, keyword):
    """Generate a hash for the prompt to use as cache key"""
    full_prompt = prompt.format(keyword=keyword)
    return hashlib.md5(full_prompt.encode()).hexdigest()

def load_from_cache(prompt_hash):
    """Load image from cache if it exists"""
    cache_file = os.path.join(CACHE_DIR, f"{prompt_hash}.png")
    if os.path.exists(cache_file):
        return cache_file
    return None

def save_to_cache(prompt_hash, image_path):
    """Save image to cache"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    cache_file = os.path.join(CACHE_DIR, f"{prompt_hash}.png")
    if os.path.exists(image_path):
        # Copy to cache
        with open(image_path, 'rb') as src, open(cache_file, 'wb') as dst:
            dst.write(src.read())


def generate_viral_thumbnail(keyword: str, output_path: str = "output/viral_thumbnail.png"):
    """
    Generates a single, viral YouTube thumbnail for a "Top 3" video.

    Args:
        keyword (str): The keyword to feature in the thumbnail.
        output_path (str): The path to save the generated thumbnail.
    """
    print(f"🎨 Generating viral 'Top 3' thumbnail for: '{keyword}'...")

    prompt = (
        "Create a wide-screen futuristic YouTube thumbnail in 16:9 format. "
        "Layout: Show a FULL ROOM VIEW from wall to wall, floor to ceiling. Three distinct {keyword} products arranged horizontally taking up 75% of the image width on the right side — make them EXTREMELY LARGE and the main focus. "
        "Human element: Place a realistic futuristic WOMAN in the BOTTOM-LEFT CORNER, framed as face and half-body, clearly larger on screen (occupying ~35% of height). She has a shocked, amazed expression and points toward the winner. Keep human features natural; add subtle futuristic accents (soft neon rim light, minimal HUD reflections) without looking robotic. "
        "Background: Complete room interior - show the CEILING with futuristic lighting panels, WALLS with holographic displays, FLOOR with neon grid patterns. Fill the top area with ceiling details, holographic text, and lighting effects. Fill the bottom area with floor patterns, reflections, and additional UI elements. "
        "Visual elements: Large red X crosses over the first two products, bright neon green checkmark with glowing 'WINNER' badge over the third product. "
        "Make the WINNER vacuum 140% larger than the other two products with explosive motion lines, a dramatic golden spotlight beam, and intense pulsating golden aura around it to make it the absolute dominant hero. "
        "Text: ULTRA-MASSIVE 'TOP 3' text at the top (40% bigger than normal) and 'TESTED IN 2025!' directly beneath it, both centered, in bright white/yellow with extra-thick black stroke and strong outer glow for perfect mobile readability. "
        "Add subheading: 'TESTED IN 2025!' in bold yellow text with extra-thick black stroke outline and bright glow for perfect contrast. "
        "Add bottom text: 'SHOCKING RESULTS!' in bold red/white with thick black stroke and subtle red glow for maximum urgency. "
        "Add small price indicators: Show '$$$' over the losing products and 'BEST VALUE' over the winner to increase purchase urgency. "
        "Style: Ultra-modern, cyberpunk aesthetic with dramatic lighting and sharp contrasts that extends to every corner of the image. "
        "Products should have premium, high-tech appearance with metallic finishes and LED accents. "
        "CRITICAL: Design for 16:9 widescreen format. Use VERTICAL SPACE efficiently: "
        "- TOP 25%: Ceiling with lighting panels, holographic displays, floating UI elements, and main title text "
        "- MIDDLE 50%: Main content area with robot, products, and core visual elements "
        "- BOTTOM 25%: Floor with neon patterns, reflections, additional text, and tech details "
        "Ensure bright, colorful elements in ALL areas to eliminate any black/dark zones."
    )

    # Check cache first to save API calls
    prompt_hash = get_prompt_hash(prompt, keyword)
    cached_image = load_from_cache(prompt_hash)
    if cached_image:
        print(f"🔄 Found cached image, copying to: {output_path}")
        with open(cached_image, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())
        return output_path

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt.format(keyword=keyword)],
            )

            if not response.candidates:
                print("❌ Error: The API response did not contain any candidates.")
                if hasattr(response, 'prompt_feedback'):
                    print(f"   - Prompt Feedback: {response.prompt_feedback}")
                if attempt < max_retries - 1:
                    print("⏳ Waiting 5 seconds before retry...")
                    time.sleep(5)
                    continue
                return None

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = BytesIO(part.inline_data.data)
                    
                    # Just resize without cropping to preserve all content
                    with Image.open(image_bytes) as img:
                        img = img.resize((1280, 720), Image.LANCZOS)
                        img.save(output_path)

                    print(f"🖼️  Viral thumbnail saved to: {output_path}")
                    
                    # Save to cache for future use
                    save_to_cache(prompt_hash, output_path)
                    print(f"💾 Cached for future use (saves API costs)")
                    
                    return output_path
            
            print("❌ Error: No image data found.")
            if attempt < max_retries - 1:
                print("⏳ Waiting 5 seconds before retry...")
                time.sleep(5)
                continue
            return None

        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("⏳ Waiting 5 seconds before retry...")
                time.sleep(5)
            else:
                print("❌ All retry attempts failed.")
                return None

if __name__ == "__main__":
    test_keyword = "vacuum cleaner"
    if not os.path.exists("output"):
        os.makedirs("output")
        
    generate_viral_thumbnail(test_keyword)
