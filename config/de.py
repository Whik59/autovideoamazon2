from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'de'
    VOICE_LANGUAGE = 'de'
    TTS_LANGUAGE_CODE = 'de-DE'

    # Amazon Scraping Settings
    AMAZON_TLD = 'de'
    AMAZON_TAG = 'clickclickh0b-21'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Sage den folgenden Text auf natürliche, klare und ansprechende Weise.'
    
    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "TITEL FÜR DIE ANZEIGE:"
    SPOKEN_NAME_LABEL = "MÜNDLICHER NAME:"
    ABOUT_THIS_ITEM_LABEL = "Über diesen Artikel"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUKTE GETESTET"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "BESTE"
    THUMBNAIL_PRICE_FROM = "ab"
    THUMBNAIL_INSTEAD_OF = "statt"
    THUMBNAIL_BEST_PRICE = "BESTER PREIS"
    THUMBNAIL_REVIEW_COUNT = "+100 Getestet"
    THUMBNAIL_BEFORE_TEXT = "VORHER"
    THUMBNAIL_AFTER_TEXT = "NACHHER"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Bestand ändert sich schnell — prüfe die Links unten für die aktuelle Verfügbarkeit."
    OVERLAY_CTA_BANNER_TEXT = "LINK UNTEN FÜR DEN BESTEN PREIS"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "Also, was ist der beste {keyword} für dich? Hier ist unser endgültiges Urteil."
    OUTRO_BEST_OVERALL = "Für maximale Leistung und professionelle Ergebnisse ist unsere erste Wahl zweifellos der {top_choice_title}."
    OUTRO_BEST_VALUE = "Aber wenn du das beste Preis-Leistungs-Verhältnis suchst, ist der Champion der {best_value_title}. Das ist eine kluge Wahl für ein kontrolliertes Budget."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "Und unglaublicherweise ist es auch das beste Preis-Leistungs-Verhältnis, das wir gefunden haben!"
    OUTRO_CALL_TO_ACTION = "Links zu diesen beiden Champions und allen anderen heute getesteten {keyword} findest du direkt unten. Danke fürs Zuschauen, vergiss nicht, für weitere Vergleiche zu abonnieren, und bis zum nächsten Mal!"
    OUTRO_FALLBACK = "Die Links zu allen Produkten findest du in der Beschreibung. Danke fürs Zuschauen und bis bald!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Sonderregel: Beginne dein SKRIPT mit einer starken Einleitung für das Video. Erwähne, dass unser Team zur Erstellung dieser 'top 3 der besten {keyword}' über 50 Modelle analysiert hat. Stelle dann das aktuelle Produkt vor."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Sonderregel: Beende dein SKRIPT mit einem Call-to-Action, in dem du erwähnst, dass durch die Verwendung der Links in der Beschreibung ein Sonderrabatt gewährt werden könnte (z.B.: 'Kleiner Tipp: Wenn Sie die Links in der Beschreibung verwenden, um ein Produkt in den Warenkorb zu legen, wird oft ein Überraschungsrabatt gewährt!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Besondere Regel: Beginnen Sie Ihr SKRIPT, indem Sie dieses Produkt als die Spitze des Rankings vorstellen, die endgültige Wahl (z.B. 'Und schließlich, an der Spitze unseres Rankings...' oder 'Um unsere Auswahl zu krönen...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} Beste {keyword} im Jahr 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Finden Sie die besten in diesem Video getesteten {keyword} 👇"
    YOUTUBE_PRODUCT_LINE = "Nr.{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Haftungsausschluss: Dieses Video und diese Beschreibung enthalten Affiliate-Links, was bedeutet, dass ich eine kleine Provision erhalte, wenn Sie auf einen der Produktlinks klicken. Dies unterstützt den Kanal und ermöglicht es uns, weiterhin Videos wie dieses zu erstellen. Vielen Dank für die Unterstützung!"
    YOUTUBE_PINNED_COMMENT = "👇 Finden Sie die besten in diesem Video getesteten {keyword} 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "VORHER"
    THUMBNAIL_AFTER_TEXT = "NACHHER"
    THUMBNAIL_URGENCY_TEXT = "NEU 2025"
    THUMBNAIL_LIMITED_TEXT = "LIMITIERT"
    THUMBNAIL_DISCOUNT_TEXT = "SPARE €{amount}!"
    THUMBNAIL_PERCENT_OFF = "{percent}% RABATT!"
    THUMBNAIL_TODAY_ONLY = "NUR HEUTE"

# To be used in scripts
Config = LanguageConfig() 