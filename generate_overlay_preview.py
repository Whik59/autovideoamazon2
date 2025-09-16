import os
from html2image import Html2Image
import base64
from config import get_config

def generate_preview(language='fr'):
    """
    Generates a preview image of the video overlay, including the revamped CTA banner.
    """
    print(f"Generating overlay preview for language: {language}")
    
    # --- Configuration ---
    try:
        Config = get_config(language)
        print("Loaded configuration.")
    except ImportError:
        print(f"ERROR: Could not load configuration for language '{language}'.")
        return

    hti = Html2Image(output_path=Config.OUTPUT_DIR)
    
    # Ensure the output directory exists
    if not os.path.exists(Config.OUTPUT_DIR):
        os.makedirs(Config.OUTPUT_DIR)
        print(f"Created directory: {Config.OUTPUT_DIR}")

    # --- Load Template and CSS ---
    try:
        with open('overlay_template.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
        with open('overlay_style.css', 'r', encoding='utf-8') as f:
            css_style = f.read()
        print("Loaded HTML template and CSS style.")
    except FileNotFoundError as e:
        print(f"ERROR: Could not find template or CSS file: {e}")
        return

    # --- Prepare Data ---
    # Use dummy data for the preview
    position = 1
    title = "Exemple de Nom de Produit Très Long"
    price = "59,99€"
    rating_text = "4.4" # Example rating
    
    # Calculate rating percentage for the stars
    try:
        rating_float = float(rating_text.replace(',', '.'))
    except ValueError:
        rating_float = 0.0
    rating_percentage = (rating_float / 5.0) * 100

    # Get CTA text from config
    info_text = Config.OVERLAY_INFO_BANNER_TEXT
    cta_text = Config.OVERLAY_CTA_BANNER_TEXT
    
    # --- Create HTML Content ---
    # This simulates the logic from step3_video_simple.py
    html_content = f"""
    <html>
    <head>
        <style>{css_style}</style>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="overlay-container">
            <!-- Top Left Title -->
            <div class="title-container" style="opacity: 1;">
                <span class="position-tag">N°{position}</span>
                <span class="title">{title}</span>
            </div>

            <!-- Top Right Price -->
            <div class="price-container" style="opacity: 1;">
                <span class="price-new">{price}</span>
                <div class="rating">
                    <div class="stars-container">
                        <div class="stars-background">★★★★★</div>
                        <div class="stars-foreground" style="width: {rating_percentage:.2f}%;">★★★★★</div>
                    </div>
                    <span class="rating-text">{rating_text}</span>
                </div>
            </div>

            <!-- Bottom Banners -->
            <div class="cta-group" style="opacity: 1;">
                <div class="info-banner">
                    {info_text}
                </div>
                <div class="cta-banner">
                    <span class="arrow">👇</span>
                    <span>{cta_text}</span>
                    <span class="arrow">👇</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    output_filename = "overlay_preview.png"
    
    print(f"Rendering overlay to '{output_filename}'...")
    
    # --- Generate Image ---
    hti.screenshot(
        html_str=html_content,
        save_as=output_filename,
        size=(1920, 1080)
    )
    
    print("-" * 50)
    print(f"SUCCESS: Preview image saved to '{os.path.join(Config.OUTPUT_DIR, output_filename)}'")
    print("Please review the image to see the new CTA banner design.")
    print("-" * 50)


if __name__ == "__main__":
    generate_preview() 