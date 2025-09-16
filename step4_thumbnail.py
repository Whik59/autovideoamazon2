"""
Step 4: AI YouTube Thumbnail Generator

Generates viral YouTube thumbnails using Google's Gemini AI models.
Supports multiple languages with localized text elements.
"""

import os
import json
from PIL import Image
import re
import time
from io import BytesIO

# Gemini import
try:
    from google import genai as _genai
    from google.genai import types
except Exception:
    _genai = None
    types = None

class ThumbnailGenerator:
    """Generates AI-powered YouTube thumbnails using Gemini."""

    def __init__(self, config, width=1280, height=720):
        self.config = config
        self.output_dir = self.config.OUTPUT_DIR
        self.width = width
        self.height = height
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Localized strings for AI prompt text elements
        self.localized_text = {
            'en': {
                'top3': 'TOP 3',
                'tested_2025': 'TESTED IN 2025!',
                'shocking': 'SHOCKING RESULTS!',
                'winner': 'WINNER',
                'best_value': 'BEST VALUE',
            },
            'de': {
                'top3': 'TOP 3',
                'tested_2025': 'GETESTET 2025!',
                'shocking': 'SCHOCKIERENDE ERGEBNISSE!',
                'winner': 'SIEGER',
                'best_value': 'BESTES PREIS-LEISTUNGS-VERHÄLTNIS',
            },
            'fr': {
                'top3': 'TOP 3',
                'tested_2025': 'TESTÉ EN 2025 !',
                'shocking': 'RÉSULTATS CHOQUANTS !',
                'winner': 'GAGNANT',
                'best_value': 'MEILLEUR RAPPORT QUALITÉ/PRIX',
            },
            'es': {
                'top3': 'TOP 3',
                'tested_2025': '¡PROBADO EN 2025!',
                'shocking': '¡RESULTADOS IMPACTANTES!',
                'winner': 'GANADOR',
                'best_value': 'MEJOR RELACIÓN CALIDAD/PRECIO',
            },
            'nl': {
                'top3': 'TOP 3',
                'tested_2025': 'GETEST IN 2025!',
                'shocking': 'SCHOKKENDE RESULTATEN!',
                'winner': 'WINNAAR',
                'best_value': 'BESTE PRIJS-KWALITEIT',
            },
            'sv': {
                'top3': 'TOPP 3',
                'tested_2025': 'TESTAD 2025!',
                'shocking': 'CHOCKERANDE RESULTAT!',
                'winner': 'VINNARE',
                'best_value': 'BÄSTA PRIS/PRESTANDA',
            },
            'pl': {
                'top3': 'TOP 3',
                'tested_2025': 'PRZETESTOWANE W 2025 R.!',
                'shocking': 'SZOKUJĄCE WYNIKI!',
                'winner': 'ZWYCIĘZCA',
                'best_value': 'NAJLEPSZY STOSUNEK JAKOŚCI DO CENY',
            },
        }

    def _get_locale(self) -> str:
        return getattr(self.config, 'CONTENT_LANGUAGE', 'en').lower()

    def _t(self, key: str) -> str:
        locale = self._get_locale()
        bundle = self.localized_text.get(locale, self.localized_text['en'])
        return bundle.get(key, self.localized_text['en'].get(key, key))

    def _get_product_context(self, keyword: str) -> str:
        """Get appropriate background context based on product keyword."""
        keyword_lower = keyword.lower()
        
        # Kitchen appliances
        if any(word in keyword_lower for word in ['mikrowelle', 'microwave', 'oven', 'toaster', 'blender', 'mixer', 'coffee', 'kettle', 'fryer']):
            return "modern kitchen counter"
        
        # Cleaning products
        elif any(word in keyword_lower for word in ['vacuum', 'cleaner', 'staubsauger', 'aspirateur', 'mop', 'broom']):
            return "clean living room"
        
        # Electronics/Tech
        elif any(word in keyword_lower for word in ['laptop', 'computer', 'phone', 'tablet', 'headphones', 'speaker', 'tv', 'monitor']):
            return "modern desk setup"
        
        # Beauty/Personal care
        elif any(word in keyword_lower for word in ['hair', 'skin', 'makeup', 'beauty', 'cream', 'shampoo']):
            return "clean bathroom vanity"
        
        # Fitness/Sports
        elif any(word in keyword_lower for word in ['fitness', 'exercise', 'gym', 'sport', 'bike', 'treadmill']):
            return "home gym"
        
        # Tools/DIY
        elif any(word in keyword_lower for word in ['drill', 'tool', 'hammer', 'saw', 'screwdriver']):
            return "workshop bench"
        
        # Automotive
        elif any(word in keyword_lower for word in ['car', 'auto', 'tire', 'oil', 'engine']):
            return "garage"
        
        # Default: clean, neutral background
        else:
            return "clean, modern interior"

    def _generate_with_gemini(self, keyword: str, output_filename: str) -> bool:
        """Generate a thumbnail with Gemini using our proven working approach."""
        if _genai is None:
            print("⚠️ Gemini client not available.")
            return False

        api_keys = getattr(self.config, 'GEMINI_API_KEYS', [])
        api_key = None
        if isinstance(api_keys, (list, tuple)) and api_keys:
            api_key = api_keys[0]
        else:
            api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            print("⚠️ No Gemini API key found.")
            return False

        # Create product-specific, contextual prompt with better visual hierarchy
        prompt = (
            f"Create a high-impact YouTube thumbnail in 16:9 format for a '{keyword.lower()}' review video. "
            f"Background: Show a realistic {self._get_product_context(keyword)} environment that naturally relates to {keyword.lower()} usage. Make it bright, clean, and modern with natural lighting. "
            f"Layout: Three distinct, futuristic-looking {keyword.lower()} products arranged prominently across the RIGHT 70% of the image, each clearly different in design and brand. Make them exceptionally large and detailed with sleek, modern designs. "
            "Human element: On the LEFT side, show a clearly visible, realistic woman (a close-up head and shoulders shot) with an expression of shock and amazement, pointing toward the winning product. "
            f"Visual hierarchy: The first two {keyword.lower()} products must have a strong RED GLOW contained around them. "
            f"The winning {keyword.lower()} should have a modern, bright GREEN GLOW with crackling energy sparks and subtle light trails. It should be 200% larger than the others and overlap them slightly. "
            f"NO badges, checkmarks, or X's. "
            f"Typography: At the top, display 'TOP 3 {keyword.lower()}' and '{self._t('tested_2025')}' in a modern, high-impact font with a metallic texture and a modern yellow-to-gold gradient. The text must be bold, 3D, and exceptionally large. The lighting on the text should perfectly match the scene's ambient light, with bright highlights and soft, realistic shadows to enhance its visibility. "
            f"Bottom text: '{self._t('shocking')}' as a solid, single phrase in a clean, bold, white font. It must have a strong, soft black shadow projected behind it to make it pop out from the background with a clear 3D effect. "
            f"Products style: All three {keyword.lower()} products should look premium and futuristic, with sleek designs and modern LED accents. Add subtle steam rising from them. "
            "Overall Style: Apply a dynamic, high-contrast color grade to the entire image with a subtle lens flare from the winning product to increase the image's visual impact. "
            "Ensure all text is large, clear, and legible on mobile. Fill the entire 16:9 frame with NO black bars."
        )

        print("🎨 Generating viral thumbnail with Gemini...")
        
        try:
            client = _genai.Client(api_key=api_key)

            # Define safety settings to prevent content blocking
            safety_settings = [
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
            ]

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-image-preview",
                        contents=[prompt],
                        config=types.GenerateContentConfig(
                            safety_settings=safety_settings
                        )
                    )
                    # If successful, break the loop
                    break
                except Exception as e:
                    if "500" in str(e) and attempt < max_retries - 1:
                        print(f"⚠️ Server error (500) encountered. Retrying in 5 seconds... ({attempt + 1}/{max_retries})")
                        time.sleep(5)
                        continue
                    else:
                        raise e
            else:
                print("❌ AI thumbnail generation failed after multiple retries.")
                return False

            if not response.candidates:
                print("❌ Error: The API response did not contain any candidates.")
                if hasattr(response, 'prompt_feedback'):
                    print(f"   - Prompt Feedback: {response.prompt_feedback}")
                return False

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = BytesIO(part.inline_data.data)
                    
                    # Just resize without cropping to preserve all content
                    with Image.open(image_bytes) as img:
                        img = img.resize((self.width, self.height), Image.LANCZOS)
                        img.save(os.path.join(self.output_dir, output_filename))

                    print(f"🖼️  Viral thumbnail saved to: {os.path.join(self.output_dir, output_filename)}")
                    return True
            
            print("❌ Error: No image data found.")
            return False

        except Exception as e:
            print(f"❌ An unexpected error occurred during thumbnail generation: {e}")
            return False

    def generate_thumbnail(self):
        print("🖼️  STEP 4: Generating AI Thumbnail")
        print("=" * 50)

        data_file = os.path.join(self.output_dir, "enhanced_product.json")
        if not os.path.exists(data_file):
            print(f"❌ Error: Enhanced data file not found at '{data_file}'.")
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keyword = data.get('keyword', 'product').upper()

        # Generate the thumbnail with sanitized filename
        safe_keyword = re.sub(r'[<>:"/\\|?*\'`]', '_', keyword.replace(' ', '_'))
        output_filename = f"thumbnail_{safe_keyword}.png"

        # Generate with AI
        success = self._generate_with_gemini(keyword, output_filename)
        if success:
            final_path = os.path.join(self.output_dir, output_filename)
            print("\n" + "="*50)
            print("🎉 NEW AI THUMBNAIL GENERATED! 🎉")
            print(f"✅ Thumbnail saved to: {final_path}")
            return
        else:
            print("❌ AI thumbnail generation failed.")
            return

if __name__ == "__main__":
    import sys
    import argparse
    from config import get_config

    parser = argparse.ArgumentParser(description="Standalone thumbnail generator for a specific language.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    # --- NEW: Add arguments for session directories ---
    parser.add_argument('--output-dir', type=str, help="Override default output directory.")
    parser.add_argument('--audio-dir', type=str, help="Override default audio directory.")
    parser.add_argument('--videos-dir', type=str, help="Override default videos directory.")
    args = parser.parse_args()

    try:
        print(f"▶️  Running Step 4 in standalone mode for language '{args.language}'")
        Config = get_config(args.language)
        print(f"✅ Loaded configuration for language: {Config.CONTENT_LANGUAGE}")

        # --- NEW: Override config paths if provided ---
        if args.output_dir:
            Config.OUTPUT_DIR = args.output_dir
            print(f"   Overriding OUTPUT_DIR: {Config.OUTPUT_DIR}")
        # audio-dir and videos-dir are not used in this script, but we accept them for consistency

        generator = ThumbnailGenerator(Config)
        generator.generate_thumbnail()

    except ImportError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)