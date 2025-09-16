"""
Step 4: YouTube Thumbnail Generator
"""

import os
import json
from html2image import Html2Image
from PIL import Image
import glob
import pathlib
import hashlib
import random
import requests
import io

class ThumbnailGenerator:
    """Generates a YouTube thumbnail using an HTML/CSS template."""

    def __init__(self, config, width=1280, height=720):
        self.config = config
        self.output_dir = self.config.OUTPUT_DIR
        self.width = width
        self.height = height
        # Drastically increased render height for a larger "safe zone"
        self.hti = Html2Image(output_path=self.output_dir, size=(width, height + 100))
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_product_image_path(self, products, product_index=0):
        """Gets the path for a specific product image by index with background removal."""
        if not products:
            return ""
            
        # Sort products by position to ensure we get the correct product
        sorted_products = sorted(products, key=lambda p: p.get('index', 99))
        
        if product_index >= len(sorted_products):
            print(f"  ⚠️ Warning: Product index {product_index + 1} not found.")
            return ""
            
        product = sorted_products[product_index]

        # New logic: find the image path in the 'downloaded_files' list
        downloaded_files = product.get('downloaded_files', [])
        for file_type, file_path in downloaded_files:
            if file_type == 'image' and os.path.exists(file_path):
                print(f"  ✅ Found product {product_index + 1} image for thumbnail: {file_path}")
                
                return pathlib.Path(os.path.abspath(file_path)).as_uri()

        print(f"  ⚠️ Warning: No 'image' type found in downloaded_files for product #{product_index + 1}.")
        return ""

    def _calculate_before_after_prices(self, products):
        """Calculate before/after prices based on the main product price."""
        if not products:
            return "€149", "€59"  # Fallback prices
        
        # Get the main product (first one)
        main_product = sorted(products, key=lambda p: p.get('index', 99))[0]
        
        # Extract price from the product
        price_str = main_product.get('price', '€59')
        
        try:
            # Remove currency symbols and clean the price string
            import re
            # Extract number from price string (handles €59.99, $59, 59€, etc.)
            price_match = re.search(r'(\d+(?:[.,]\d+)?)', price_str.replace(',', '.'))
            
            if price_match:
                current_price = float(price_match.group(1))
                
                # Calculate before price (current price + 40%)
                before_price_value = current_price * 1.4
                
                # Determine currency symbol from original price
                currency = '€'  # Default
                if '$' in price_str:
                    currency = '$'
                elif '£' in price_str:
                    currency = '£'
                elif '€' in price_str:
                    currency = '€'
                elif 'zł' in price_str:
                    currency = 'zł'
                elif 'kr' in price_str:
                    currency = 'kr'
                
                # Format prices (round to nearest whole number for cleaner look)
                if currency in ['zł', 'kr']:
                    # For Polish Zloty and Swedish Krona, put currency after
                    before_price = f"{int(round(before_price_value))}{currency}"
                    after_price = f"{int(round(current_price))}{currency}"
                else:
                    # For Euro, Dollar, Pound, put currency before
                    before_price = f"{currency}{int(round(before_price_value))}"
                    after_price = f"{currency}{int(round(current_price))}"
                
                print(f"  💰 Calculated prices - Before: {before_price}, After: {after_price}")
                return before_price, after_price
            
        except (ValueError, AttributeError) as e:
            print(f"  ⚠️ Warning: Could not parse price '{price_str}': {e}")
        
        # Fallback to default prices if parsing fails
        return "€149", "€59"

    def _calculate_discount_text(self, products):
        """Calculate discount text for the discount badge."""
        if not products:
            return "30% RABATT!" if hasattr(self.config, 'THUMBNAIL_PERCENT_OFF') else "30% OFF!"
        
        # Get the main product (first one)
        main_product = sorted(products, key=lambda p: p.get('index', 99))[0]
        
        # Extract price from the product
        price_str = main_product.get('price', '€59')
        
        try:
            # Remove currency symbols and clean the price string
            import re
            # Extract number from price string (handles €59.99, $59, 59€, etc.)
            price_match = re.search(r'(\d+(?:[.,]\d+)?)', price_str.replace(',', '.'))
            
            if price_match:
                current_price = float(price_match.group(1))
                
                # Calculate before price (current price + 40%)
                before_price_value = current_price * 1.4
                discount_amount = before_price_value - current_price
                discount_percentage = int(round((discount_amount / before_price_value) * 100))
                
                # Determine currency symbol and format
                if 'zł' in price_str:
                    discount_text = self.config.THUMBNAIL_DISCOUNT_TEXT.format(amount=int(round(discount_amount)))
                elif 'kr' in price_str:
                    discount_text = self.config.THUMBNAIL_DISCOUNT_TEXT.format(amount=int(round(discount_amount)))
                elif '$' in price_str:
                    discount_text = self.config.THUMBNAIL_DISCOUNT_TEXT.format(amount=int(round(discount_amount)))
                else:
                    # Default to percentage for Euro and other currencies
                    discount_text = self.config.THUMBNAIL_PERCENT_OFF.format(percent=discount_percentage)
                
                print(f"  💰 Calculated discount - Amount: {int(round(discount_amount))}, Percentage: {discount_percentage}%, Text: {discount_text}")
                return discount_text
            
        except (ValueError, AttributeError) as e:
            print(f"  ⚠️ Warning: Could not parse price for discount '{price_str}': {e}")
        
        # Fallback to percentage discount
        if hasattr(self.config, 'THUMBNAIL_PERCENT_OFF'):
            return self.config.THUMBNAIL_PERCENT_OFF.format(percent=30)
        else:
            return "30% OFF!"
    
    def _generate_color_scheme(self, keyword):
        """Generate a varied color scheme that changes with each generation."""
        # Use keyword hash combined with current timestamp for maximum variation
        import time
        hash_object = hashlib.md5((keyword + str(time.time())).encode())  # Changes every generation
        hash_hex = hash_object.hexdigest()
        
        # Convert hash to seed for randomization
        seed = int(hash_hex[:8], 16)
        random.seed(seed)
        
        # Define stylish color scheme variations with modern gradients
        color_schemes = [
            {
                "name": "Neon Sunset",
                "gradient": "linear-gradient(135deg, #FF0080 0%, #FF4500 20%, #FF8C00 40%, #FFD700 60%, rgba(255, 215, 0, 0.3) 75%, rgba(255, 140, 0, 0.1) 85%, transparent 95%)",
                "accent": "#FF0080"
            },
            {
                "name": "Electric Ocean",
                "gradient": "linear-gradient(135deg, #00D4FF 0%, #0099FF 20%, #0066FF 40%, #3366FF 60%, rgba(51, 102, 255, 0.3) 75%, rgba(0, 153, 255, 0.1) 85%, transparent 95%)",
                "accent": "#00D4FF"
            },
            {
                "name": "Cosmic Purple",
                "gradient": "linear-gradient(135deg, #8A2BE2 0%, #9932CC 20%, #DA70D6 40%, #FF69B4 60%, rgba(255, 105, 180, 0.3) 75%, rgba(218, 112, 214, 0.1) 85%, transparent 95%)",
                "accent": "#8A2BE2"
            },
            {
                "name": "Neon Jungle",
                "gradient": "linear-gradient(135deg, #00FF88 0%, #00CC66 20%, #32CD32 40%, #7FFF00 60%, rgba(127, 255, 0, 0.3) 75%, rgba(50, 205, 50, 0.1) 85%, transparent 95%)",
                "accent": "#00FF88"
            },
            {
                "name": "Fire Storm",
                "gradient": "linear-gradient(135deg, #FF0000 0%, #FF4500 20%, #FF6347 40%, #FF8C00 60%, rgba(255, 140, 0, 0.3) 75%, rgba(255, 99, 71, 0.1) 85%, transparent 95%)",
                "accent": "#FF0000"
            },
            {
                "name": "Miami Vice",
                "gradient": "linear-gradient(135deg, #FF1493 0%, #FF69B4 20%, #FF6347 40%, #FFA500 60%, rgba(255, 165, 0, 0.3) 75%, rgba(255, 99, 71, 0.1) 85%, transparent 95%)",
                "accent": "#FF1493"
            },
            {
                "name": "Cyber Matrix",
                "gradient": "linear-gradient(135deg, #00FFFF 0%, #00CED1 20%, #20B2AA 40%, #48D1CC 60%, rgba(72, 209, 204, 0.3) 75%, rgba(32, 178, 170, 0.1) 85%, transparent 95%)",
                "accent": "#00FFFF"
            },
            {
                "name": "Golden Hour",
                "gradient": "linear-gradient(135deg, #FFD700 0%, #FFA500 20%, #FF8C00 40%, #FF6347 60%, rgba(255, 99, 71, 0.3) 75%, rgba(255, 140, 0, 0.1) 85%, transparent 95%)",
                "accent": "#FFD700"
            },
            {
                "name": "Arctic Aurora",
                "gradient": "linear-gradient(135deg, #00BFFF 0%, #1E90FF 20%, #4169E1 40%, #6495ED 60%, rgba(100, 149, 237, 0.3) 75%, rgba(30, 144, 255, 0.1) 85%, transparent 95%)",
                "accent": "#00BFFF"
            },
            {
                "name": "Toxic Glow",
                "gradient": "linear-gradient(135deg, #ADFF2F 0%, #7FFF00 20%, #32CD32 40%, #00FF7F 60%, rgba(0, 255, 127, 0.3) 75%, rgba(50, 205, 50, 0.1) 85%, transparent 95%)",
                "accent": "#ADFF2F"
            }
        ]
        
        # Select scheme based on hash
        scheme_index = seed % len(color_schemes)
        selected_scheme = color_schemes[scheme_index]
        
        print(f"  🎨 Selected color scheme: {selected_scheme['name']} for keyword '{keyword}'")
        return selected_scheme
    
    def _remove_background(self, image_path):
        """Remove background from product image using rembg library."""
        try:
            # Check if background-removed version already exists
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_nobg.png")
            
            if os.path.exists(output_path):
                print(f"  ✅ Using existing background-removed image: {output_path}")
                return output_path
            
            # Import and use rembg
            from rembg import remove, new_session
            print(f"  🎯 Removing background from image using rembg...")
            
            # Create a session for better performance
            session = new_session('u2net')
            
            # Read the image
            with open(image_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # Remove background
            output_data = remove(input_data, session=session)
            
            # Save the result
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
            
            print(f"  ✅ Background removed successfully: {output_path}")
            return output_path
                
        except ImportError as e:
            print(f"  ⚠️ rembg import failed: {e}")
            print(f"  📝 Using original image with white background")
            return image_path
        except Exception as e:
            print(f"  ⚠️ Background removal failed: {e}")
            print(f"  📝 Using original image")
            return image_path

    def generate_thumbnail(self):
        print("🖼️  STEP 4: Generating Thumbnail with HTML/CSS")
        print("=" * 50)

        data_file = os.path.join(self.output_dir, "enhanced_product.json")
        if not os.path.exists(data_file):
            print(f"❌ Error: Enhanced data file not found at '{data_file}'.")
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keyword = data.get('keyword', 'product').upper()

        products = data.get('products', [])
        
        product_image_uri = self._get_product_image_path(products, 0)  # First product
        product2_image_uri = self._get_product_image_path(products, 1)  # Second product
        product3_image_uri = self._get_product_image_path(products, 2)  # Third product
        
        if not product_image_uri:
            print(f"❌ Error: Could not find any product or fallback image to use.")
            return

        # Avatar removed for shadowban prevention
        avatar_uri = ""
            
        emoji_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "emoji.png"))
        if os.path.exists(emoji_path):
            emoji_uri = pathlib.Path(emoji_path).as_uri()
        else:
            print("  ⚠️ Emoji image not found. It will be omitted.")
            emoji_uri = ""

        icon_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "icon.png"))
        if os.path.exists(icon_path):
            icon_uri = pathlib.Path(icon_path).as_uri()
        else:
            print("  ⚠️ Icon image not found. It will be omitted.")
            icon_uri = ""

        stars_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "5stars.webp"))
        if os.path.exists(stars_path):
            stars_uri = pathlib.Path(stars_path).as_uri()
        else:
            print("  ⚠️ Stars image not found. It will be omitted.")
            stars_uri = ""

        checkmark_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "checkmark.webp"))
        if os.path.exists(checkmark_path):
            checkmark_uri = pathlib.Path(checkmark_path).as_uri()
        else:
            print("  ⚠️ Checkmark image not found. It will be omitted.")
            checkmark_uri = ""

        arrow_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "arrow.png"))
        if os.path.exists(arrow_path):
            arrow_uri = pathlib.Path(arrow_path).as_uri()
        else:
            print("  ⚠️ Arrow image not found. It will be omitted.")
            arrow_uri = ""

        redcross_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "redcross.png"))
        if os.path.exists(redcross_path):
            redcross_uri = pathlib.Path(redcross_path).as_uri()
        else:
            print("  ⚠️ Red cross image not found. It will be omitted.")
            redcross_uri = ""

        greentick_path = os.path.abspath(os.path.join(self.config.THUMBNAIL_DIR, "greentick.png"))
        if os.path.exists(greentick_path):
            greentick_uri = pathlib.Path(greentick_path).as_uri()
        else:
            print("  ⚠️ Green tick image not found. It will be omitted.")
            greentick_uri = ""

        # Read HTML template
        try:
            with open('thumbnail_template.html', 'r', encoding='utf-8') as f:
                html_template = f.read()
        except FileNotFoundError:
            print("❌ Error: `thumbnail_template.html` not found.")
            return

        # --- SIMPLE: Character-based font size calculation ---
        def get_font_size_by_length(text):
            """
            Simple character-based font size calculation for Anton font.
            Ensures text always fits on one line regardless of content.
            """
            char_count = len(text)
            print(f"  📝 Text: '{text}' ({char_count} characters)")
            
            # --- MODIFIED: Font sizes reduced slightly for a less prominent look ---
            if char_count <= 15:
                font_size = 115
            elif char_count <= 20:
                font_size = 95
            elif char_count <= 25:
                font_size = 80
            elif char_count <= 30:
                font_size = 65
            elif char_count <= 35:
                font_size = 55
            else:
                font_size = 45
            
            print(f"  📏 Font size for {char_count} chars: {font_size}px")
            return font_size

        # Calculate font size based on keyword length
        keyword_text = f"{keyword} 2025"
        keyword_font_size = get_font_size_by_length(keyword_text)
        keyword_style = f"font-size: {keyword_font_size}px;"
        
        # Generate dynamic color scheme based on keyword
        color_scheme = self._generate_color_scheme(keyword)
        background_gradient = color_scheme["gradient"]

        # Inject data into HTML
        html_content = html_template.replace("{{product_image_path}}", product_image_uri)
        html_content = html_content.replace("{{keyword}}", keyword)
        html_content = html_content.replace("{{keyword_text}}", keyword_text)  # Add keyword_text replacement
        html_content = html_content.replace("{{keyword_style}}", keyword_style) # New line for dynamic style
        html_content = html_content.replace("{{avatar_image_path}}", avatar_uri)
        html_content = html_content.replace("{{emoji_image_path}}", emoji_uri)
        html_content = html_content.replace("{{icon_image_path}}", icon_uri)
        html_content = html_content.replace("{{stars_image_path}}", stars_uri)
        html_content = html_content.replace("{{checkmark_image_path}}", checkmark_uri)
        html_content = html_content.replace("{{arrow_image_path}}", arrow_uri)
        html_content = html_content.replace("{{redcross_image_path}}", redcross_uri)
        html_content = html_content.replace("{{greentick_image_path}}", greentick_uri)
        html_content = html_content.replace("{{product2_image_path}}", product2_image_uri)
        html_content = html_content.replace("{{product3_image_path}}", product3_image_uri)
        html_content = html_content.replace("{{ thumbnail_subtitle }}", self.config.THUMBNAIL_SUBTITLE)
        html_content = html_content.replace("{{top_text}}", self.config.THUMBNAIL_TOP_TEXT)
        html_content = html_content.replace("{{best_text}}", self.config.THUMBNAIL_BEST_TEXT)
        html_content = html_content.replace("{{price_from}}", self.config.THUMBNAIL_PRICE_FROM)
        html_content = html_content.replace("{{instead_of}}", self.config.THUMBNAIL_INSTEAD_OF)
        html_content = html_content.replace("{{best_price_text}}", self.config.THUMBNAIL_BEST_PRICE)
        html_content = html_content.replace("{{review_count}}", self.config.THUMBNAIL_REVIEW_COUNT)
        html_content = html_content.replace("{{before_text}}", self.config.THUMBNAIL_BEFORE_TEXT)
        html_content = html_content.replace("{{after_text}}", self.config.THUMBNAIL_AFTER_TEXT)
        html_content = html_content.replace("{{urgency_text}}", self.config.THUMBNAIL_URGENCY_TEXT)
        html_content = html_content.replace("{{today_only_text}}", self.config.THUMBNAIL_TODAY_ONLY)
        
        # Calculate dynamic before/after prices based on the main product
        before_price, after_price = self._calculate_before_after_prices(products)
        html_content = html_content.replace("{{before_price}}", before_price)
        html_content = html_content.replace("{{after_price}}", after_price)
        
        # Calculate and add discount text
        discount_text = self._calculate_discount_text(products)
        html_content = html_content.replace("{{discount_text}}", discount_text)
        
        # Inject dynamic color scheme
        html_content = html_content.replace("{{background_gradient}}", background_gradient)

        # Generate the thumbnail with sanitized filename
        import re
        # Sanitize keyword for filename - remove/replace problematic characters
        safe_keyword = re.sub(r'[<>:"/\\|?*\'`]', '_', keyword.replace(' ', '_'))
        output_filename = f"thumbnail_{safe_keyword}.png"
        
        print("\n⏳ Rendering HTML to image... (This may take a moment)")
        self.hti.screenshot(
            html_str=html_content,
            css_file='thumbnail_style.css', # Use the updated external CSS file
            save_as=output_filename
        )
        
        final_path = os.path.join(self.output_dir, output_filename)

        # Precisely crop the over-rendered image to the exact dimensions
        print("   ...cropping to final dimensions to guarantee no cut-offs.")
        try:
            with Image.open(final_path) as img:
                crop_box = (0, 0, self.width, self.height)
                cropped_img = img.crop(crop_box)
                cropped_img.save(final_path, 'PNG', quality=95)
        except Exception as e:
            print(f"❌ Error during final cropping step: {e}")
            return

        print("\n" + "="*50)
        print("🎉 NEW PROFESSIONAL THUMBNAIL GENERATED! 🎉")
        print(f"✅ Thumbnail saved to: {final_path}")

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