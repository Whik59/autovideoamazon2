import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # TTS Provider Settings
    TTS_PROVIDER = os.getenv('TTS_PROVIDER', 'gemini-tts')  # 'gcloud' or 'gemini-tts'
    TTS_LANGUAGE_CODE = os.getenv('TTS_LANGUAGE_CODE', 'fr-FR')
    TTS_SPEAKING_RATE = float(os.getenv('TTS_SPEAKING_RATE', '1.0'))  # 0.25 - 2.0

    # Gemini TTS Settings
    GEMINI_TTS_MODEL = os.getenv('GEMINI_TTS_MODEL', 'gemini-2.5-flash-preview-tts')  # Using pro for better quotas
    # --- DEPRECATED: The single voice setting is now replaced by the voice mapping below ---
    # GEMINI_TTS_VOICE = os.getenv('GEMINI_TTS_VOICE', 'Sulafat')
    GEMINI_TTS_PROMPT = os.getenv('GEMINI_TTS_PROMPT', 'Dis le texte suivant de manière naturelle, claire et engageante.')

    # --- NEW: Voice mapping for different products ---
    # Defines which voice to use for each product position.
    # The key is the product position (e.g., 3, 2, 1).
    # You can define a 'default' voice for any position not explicitly listed.
    GEMINI_TTS_VOICE_MAPPING = {
        3: 'Sulafat',  # Woman
        2: 'Alnilam',  # Man
        1: 'Sulafat',  # Woman
        'default': 'Sulafat'
    }
    
    # Language Settings
    CONTENT_LANGUAGE = os.getenv('CONTENT_LANGUAGE', 'fr')  # French by default
    VOICE_LANGUAGE = os.getenv('VOICE_LANGUAGE', 'fr')      # French voice
    
    # Amazon Scraping Settings
    AMAZON_TLD = os.getenv('AMAZON_TLD', 'fr')
    AMAZON_TAG = os.getenv('AMAZON_TAG', 'clickclickh01-21')
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 2
    PRODUCTS_PER_KEYWORD = 3  # Changed from 5 to 3 for faster processing
    
    # Video Settings
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    VIDEO_FPS = 30
    PRODUCT_DISPLAY_TIME = 8  # seconds per product
    TRANSITION_DURATION = 1.5
    BACKGROUND_MUSIC_PATH = os.getenv('BACKGROUND_MUSIC_PATH', 'thumbnail/bgmusic.mp3')
    BACKGROUND_MUSIC_VOLUME = float(os.getenv('BACKGROUND_MUSIC_VOLUME', '0.05')) # 5% volume
    
    # --- NEW --- Hardware Acceleration Settings
    # Use 'h264_nvenc' for NVIDIA, 'h264_amf' for AMD, or 'libx264' for CPU
    VIDEO_ENCODER = os.getenv('VIDEO_ENCODER', 'libx264') 
    # Preset for CPU encoding. 'ultrafast' is fastest.
    CPU_ENCODER_PRESET = os.getenv('CPU_ENCODER_PRESET', 'ultrafast')
    
    # Output Settings
    OUTPUT_DIR = "output"
    TEMP_DIR = "temp"
    AUDIO_DIR = "audio"
    IMAGES_DIR = "images"
    VIDEOS_DIR = "videos"
    THUMBNAIL_DIR = "thumbnail"
    
    # YouTube Settings
    YOUTUBE_CATEGORY_ID = "22"  # People & Blogs
    YOUTUBE_PRIVACY_STATUS = "public"
    
    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Default - You must add the item to your cart for the discount to apply!"
    OVERLAY_CTA_BANNER_TEXT = "-30% LINK BELOW"

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "DISPLAY TITLE:"
    SPOKEN_NAME_LABEL = "SPOKEN NAME:"
    ABOUT_THIS_ITEM_LABEL = "About this item"

    # --- NEW: Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUCTS TESTED"

    # --- DEPRECATED: Outro Text ---
    OUTRO_LEAD_IN = ""
    OUTRO_BEST_OVERALL = ""
    OUTRO_BEST_VALUE = ""
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = ""
    OUTRO_CALL_TO_ACTION = ""
    OUTRO_FALLBACK = ""

    # --- DEPRECATED: Special Instructions ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = ""
    SPECIAL_INSTRUCTIONS_POSITION_3 = ""
    SPECIAL_INSTRUCTIONS_POSITION_1 = ""

    # User Agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    ] 

    # --- NEW: API Key Rotation ---
    # Add all your Gemini API keys to this list. The pipeline will rotate through them.
    GEMINI_API_KEYS = [
        "AIzaSyAz-2QpjTB17-iJNVGZm1DRVO6HUmxV6rg",
        "AIzaSyBdYz04o9vVORDLQ56eDGwMEFpjccIGWtQ",
        
        # "YOUR_SECOND_API_KEY_HERE",
        # "YOUR_THIRD_API_KEY_HERE",
    ]

    # --- Gemini TTS Settings ---
    GEMINI_TTS_PROMPT = 'Say the following text in a natural, clear, and engaging way.'

    # --- Thumbnail Settings --- 

    # --- NEW: Anti-Detect Browser Profile Mapping ---
    # Maps a YouTube channel name to the name of the anti-detect browser profile.
    # This ensures that when authentication is required, the correct browser
    # profile is launched for the login process.
    # Example:
    # CHANNEL_TO_PROFILE_MAPPING = {
    #     "frenchchannel1": "frenchprofile",
    #     "frenchchannel2": "frenchprofile",
    #     "germanchannel1": "germanprofile",
    # }
    CHANNEL_TO_PROFILE_MAPPING = {
        # French channels using the "top3french" anti-detect profile
        "top3cuisine": "top3french",
        "top3café": "top3french",
        # Add your other channels here...
    } 