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
except Exception:
    _genai = None

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
            f"Layout: Three distinct, futuristic-looking {keyword.lower()} products arranged prominently across the RIGHT 70% of the image, each clearly different in design and brand. Make them VERY LARGE and detailed with sleek, modern designs. "
            "Human element: On the LEFT side, show a realistic woman (face and upper body) with a genuinely shocked, amazed expression pointing toward the winning product. Natural lighting, authentic human emotion. "
            f"Visual hierarchy: The first two {keyword.lower()} products must have a strong RED GLOW that is CONTAINED around them and does not spill onto other parts of the image, especially the woman. "
            f"The winning {keyword.lower()} should have an intense, bright GREEN GLOW with crackling energy sparks, be 160% larger than the others, and slightly overlap them to show dominance. "
            f"NO badges, NO checkmarks, NO X's - only use contained glows. "
            f"Typography: 'TOP 3 {keyword.lower()}' and '{self._t('tested_2025')}' text as a single, HUGE, ultra-futuristic, glowing holographic banner integrated into the top background. Make this banner and the text within it 20% larger than before, with stylized letters and dynamic light effects for maximum impact. "
            f"Bottom text: '{self._t('shocking')}' as a holographic projection onto the kitchen counter or as a subtle, semi-transparent overlay at the very bottom, integrated with the scene's lighting. "
            f"Products style: Make the three {keyword.lower()} products look distinct, premium, and highly futuristic - emphasize unique, sleek designs, metallic chrome finishes, vibrant LED accents, and cutting-edge modern styling. Each product must appear visually different from the others. "
            "Lighting: Ensure all elements (woman, products, text) are lit consistently from the same light sources within the kitchen scene for maximum realism and cohesion. "
            "Ensure all text is large and clear for mobile. Fill the entire 16:9 frame with NO black bars."
        )

        print("🎨 Generating viral thumbnail with Gemini...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
                client = _genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image-preview",
                    contents=[prompt],
                )

                if not response.candidates:
                    print("❌ Error: The API response did not contain any candidates.")
                    if hasattr(response, 'prompt_feedback'):
                        print(f"   - Prompt Feedback: {response.prompt_feedback}")
                    if attempt < max_retries - 1:
                        print("⏳ Waiting 5 seconds before retry...")
                        time.sleep(5)
                        continue
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
                if attempt < max_retries - 1:
                    print("⏳ Waiting 5 seconds before retry...")
                    time.sleep(5)
                    continue
                return False

            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("⏳ Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    print("❌ All retry attempts failed.")
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
    args = parser.parse_args()

    try:
        print(f"▶️  Running Step 4 in standalone mode for language '{args.language}'")
        Config = get_config(args.language)
        print(f"✅ Loaded configuration for language: {Config.CONTENT_LANGUAGE}")

        generator = ThumbnailGenerator(Config)
        generator.generate_thumbnail()

    except ImportError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)