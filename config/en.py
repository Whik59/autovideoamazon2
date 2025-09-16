from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'en'
    VOICE_LANGUAGE = 'en'
    TTS_LANGUAGE_CODE = 'en-US'

    # Amazon Scraping Settings
    AMAZON_TLD = 'com'
    AMAZON_TAG = 'natdurdenusa-20'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Say the following text in a natural, clear, and engaging way.'

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "DISPLAY TITLE:"
    SPOKEN_NAME_LABEL = "SPOKEN NAME:"
    ABOUT_THIS_ITEM_LABEL = "About this item"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUCTS TESTED"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "BEST"
    THUMBNAIL_PRICE_FROM = "from"
    THUMBNAIL_INSTEAD_OF = "instead of"
    THUMBNAIL_BEST_PRICE = "BEST PRICE"
    THUMBNAIL_REVIEW_COUNT = "+100 Tested"
    THUMBNAIL_BEFORE_TEXT = "BEFORE"
    THUMBNAIL_AFTER_TEXT = "AFTER"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Stock changes fast — check the links below for current availability."
    OVERLAY_CTA_BANNER_TEXT = "LINK BELOW FOR THE BEST PRICE"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "So, what's the best {keyword} for you? Here's our final verdict."
    OUTRO_BEST_OVERALL = "For maximum performance and professional results, our number one choice is hands-down the {top_choice_title}."
    OUTRO_BEST_VALUE = "But if you're looking for the best value for money, the champion is the {best_value_title}. It's a smart choice for a controlled budget."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "And incredibly, it's also the best value we've found!"
    OUTRO_CALL_TO_ACTION = "Links to these two champions and all the other {keyword} tested today are just below. Thanks for watching, don't forget to subscribe for more comparisons, and see you next time!"
    OUTRO_FALLBACK = "You can find the links to all the products in the description. Thanks for watching and see you soon!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Special Rule: Start your SCRIPT with a powerful introduction for the video. Mention that to establish this 'top 3 best {keyword}', our team analyzed over 50 models. Then, introduce the current product."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Special Rule: End your SCRIPT with a call to action mentioning that by using the links in the description, a special discount might be applied (e.g., 'Quick tip: by using the links in the description to add a product to the cart, a surprise discount is often applied!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Special Rule: Start your SCRIPT by introducing this product as the top of the ranking, the final choice (e.g., 'And finally, at the top of our ranking...' or 'To crown our selection...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} Best {keyword} in 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Find the best {keyword} tested in this video 👇"
    YOUTUBE_PRODUCT_LINE = "N°{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Disclaimer: This video and description contain affiliate links, which means that if you click on one of the product links, I’ll receive a small commission. This helps support the channel and allows us to continue to make videos like this. Thank you for the support!"
    YOUTUBE_PINNED_COMMENT = "👇 Find the best {keyword} tested in this video 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "BEFORE"
    THUMBNAIL_AFTER_TEXT = "AFTER"
    THUMBNAIL_URGENCY_TEXT = "NEW 2025"
    THUMBNAIL_LIMITED_TEXT = "LIMITED"
    THUMBNAIL_DISCOUNT_TEXT = "SAVE ${amount}!"
    THUMBNAIL_PERCENT_OFF = "{percent}% OFF NOW!"
    THUMBNAIL_TODAY_ONLY = "TODAY ONLY"

# To be used in scripts
Config = LanguageConfig() 