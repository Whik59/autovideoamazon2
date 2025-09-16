from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'nl'
    VOICE_LANGUAGE = 'nl'
    TTS_LANGUAGE_CODE = 'nl-NL'

    # Amazon Scraping Settings
    AMAZON_TLD = 'nl'
    AMAZON_TAG = 'clickclickh0a-21'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Zeg de volgende tekst op een natuurlijke, duidelijke en boeiende manier.'

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "WEERGAVETITEL:"
    SPOKEN_NAME_LABEL = "GESPROKEN NAAM:"
    ABOUT_THIS_ITEM_LABEL = "Over dit artikel"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUCTEN GETEST"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "BESTE"
    THUMBNAIL_PRICE_FROM = "vanaf"
    THUMBNAIL_INSTEAD_OF = "in plaats van"
    THUMBNAIL_BEST_PRICE = "BESTE PRIJS"
    THUMBNAIL_REVIEW_COUNT = "+100 Getest"
    THUMBNAIL_BEFORE_TEXT = "VOOR"
    THUMBNAIL_AFTER_TEXT = "NA"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Voorraad verandert snel — controleer de links hieronder voor de actuele beschikbaarheid."
    OVERLAY_CTA_BANNER_TEXT = "LINK HIERONDER VOOR DE BESTE PRIJS"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "Dus, wat is de beste {keyword} voor jou? Hier is ons definitieve oordeel."
    OUTRO_BEST_OVERALL = "Voor maximale prestaties en professionele resultaten is onze nummer één keuze zonder twijfel de {top_choice_title}."
    OUTRO_BEST_VALUE = "Maar als je op zoek bent naar de beste prijs-kwaliteitverhouding, is de kampioen de {best_value_title}. Het is een slimme keuze voor een beperkt budget."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "En ongelooflijk, het is ook de beste prijs-kwaliteitverhouding die we hebben gevonden!"
    OUTRO_CALL_TO_ACTION = "Links naar deze twee kampioenen en alle andere {keyword} die vandaag zijn getest, vind je hieronder. Bedankt voor het kijken, vergeet je niet te abonneren voor meer vergelijkingen, en tot de volgende keer!"
    OUTRO_FALLBACK = "Je kunt de links naar alle producten in de beschrijving vinden. Bedankt voor het kijken en tot ziens!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Speciale Regel: Begin je SCRIPT met een krachtige inleiding voor de video. Vermeld dat ons team om deze 'top 3 beste {keyword}' vast te stellen, meer dan 50 modellen heeft geanalyseerd. Introduceer vervolgens het huidige product."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Speciale Regel: Beëindig je SCRIPT met een call-to-action waarin wordt vermeld dat door de links in de beschrijving te gebruiken, een speciale korting kan worden toegepast (bijv. 'Kleine tip: door de links in de beschrijving te gebruiken om een product aan het winkelwagentje toe te voegen, wordt vaak een verrassingskorting toegepast!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Speciale Regel: Begin je SCRIPT door dit product te introduceren als de top van de ranglijst, de uiteindelijke keuze (bijv. 'En tot slot, aan de top van onze ranglijst...' of 'Om onze selectie te bekronen...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} Beste {keyword} in 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Vind de beste {keyword} getest in deze video 👇"
    YOUTUBE_PRODUCT_LINE = "Nr.{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Disclaimer: Deze video en beschrijving bevatten affiliate links, wat betekent dat als je op een van de productlinks klikt, ik een kleine commissie ontvang. Dit helpt het kanaal te ondersteunen en stelt ons in staat om door te gaan met het maken van video's zoals deze. Bedankt voor de steun!"
    YOUTUBE_PINNED_COMMENT = "👇 Vind de beste {keyword} getest in deze video 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "VOOR"
    THUMBNAIL_AFTER_TEXT = "NA"
    THUMBNAIL_URGENCY_TEXT = "NIEUW 2025"
    THUMBNAIL_LIMITED_TEXT = "BEPERKT"
    THUMBNAIL_DISCOUNT_TEXT = "BESPAAR €{amount}!"
    THUMBNAIL_PERCENT_OFF = "{percent}% KORTING!"
    THUMBNAIL_TODAY_ONLY = "ALLEEN VANDAAG"

# To be used in scripts
Config = LanguageConfig()