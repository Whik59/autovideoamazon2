from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'sv'
    VOICE_LANGUAGE = 'sv'
    TTS_LANGUAGE_CODE = 'sv-SE'

    # Amazon Scraping Settings
    AMAZON_TLD = 'se'
    AMAZON_TAG = 'clickclickh0e-21'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Säg följande text på ett naturligt, tydligt och engagerande sätt.'

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "VISNINGSTITEL:"
    SPOKEN_NAME_LABEL = "TALNAMN:"
    ABOUT_THIS_ITEM_LABEL = "Om denna artikel"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUKTER TESTADE"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "BÄSTA"
    THUMBNAIL_PRICE_FROM = "från"
    THUMBNAIL_INSTEAD_OF = "istället för"
    THUMBNAIL_BEST_PRICE = "BÄSTA PRIS"
    THUMBNAIL_REVIEW_COUNT = "+100 Testade"
    THUMBNAIL_BEFORE_TEXT = "INNAN"
    THUMBNAIL_AFTER_TEXT = "EFTER"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Lagret ändras snabbt — kontrollera länkarna nedan för aktuell tillgänglighet."
    OVERLAY_CTA_BANNER_TEXT = "LÄNK NEDAN FÖR BÄSTA PRIS"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "Så, vilken är den bästa {keyword} för dig? Här är vårt slutgiltiga utlåtande."
    OUTRO_BEST_OVERALL = "För maximal prestanda och professionella resultat är vårt förstahandsval utan tvekan {top_choice_title}."
    OUTRO_BEST_VALUE = "Men om du letar efter det bästa värdet för pengarna är mästaren {best_value_title}. Det är ett smart val för en kontrollerad budget."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "Och otroligt nog är det också det bästa värdet vi har hittat!"
    OUTRO_CALL_TO_ACTION = "Länkar till dessa två mästare och alla andra {keyword} som testats idag finns precis nedanför. Tack för att du tittade, glöm inte att prenumerera för fler jämförelser, och vi ses nästa gång!"
    OUTRO_FALLBACK = "Du hittar länkarna till alla produkter i beskrivningen. Tack för att du tittade och vi ses snart!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Särskild Regel: Börja ditt MANUS med en kraftfull introduktion för videon. Nämn att för att skapa denna 'Topp 5 bästa {keyword}' analyserade vårt team över 50 modeller. Presentera sedan den aktuella produkten."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Särskild Regel: Avsluta ditt MANUS med en uppmaning till handling där du nämner att genom att använda länkarna i beskrivningen kan en särskild rabatt tillämpas (t.ex. 'Litet tips: genom att använda länkarna i beskrivningen för att lägga en produkt i varukorgen tillämpas ofta en överraskningsrabatt!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Särskild Regel: Börja ditt SCRIPT med att introducera denna produkt som toppen av rankningen, det slutgiltiga valet (t.ex. 'Och slutligen, högst upp på vår ranking...' eller 'För att kröna vårt urval...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Topp {product_count} Bästa {keyword} 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Hitta de bästa {keyword} som testats i den här videon 👇"
    YOUTUBE_PRODUCT_LINE = "Nr.{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Ansvarsfriskrivning: Denna video och beskrivning innehåller affiliatelänkar, vilket innebär att om du klickar på en av produktlänkarna får jag en liten provision. Detta hjälper till att stödja kanalen och gör att vi kan fortsätta göra videor som denna. Tack för stödet!"
    YOUTUBE_PINNED_COMMENT = "👇 Hitta de bästa {keyword} som testats i den här videon 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "FÖRE"
    THUMBNAIL_AFTER_TEXT = "EFTER"
    THUMBNAIL_URGENCY_TEXT = "NY 2025"
    THUMBNAIL_LIMITED_TEXT = "BEGRÄNSAD"
    THUMBNAIL_DISCOUNT_TEXT = "SPARA {amount}kr!"
    THUMBNAIL_PERCENT_OFF = "{percent}% RABATT!"
    THUMBNAIL_TODAY_ONLY = "ENDAST IDAG"

# To be used in scripts
Config = LanguageConfig()