from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'it'
    VOICE_LANGUAGE = 'it'
    TTS_LANGUAGE_CODE = 'it-IT'

    # Amazon Scraping Settings
    AMAZON_TLD = 'it'
    AMAZON_TAG = 'clickclickh09-21'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Pronuncia il seguente testo in modo naturale, chiaro e coinvolgente.'

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "TITOLO DI VISUALIZZAZIONE:"
    SPOKEN_NAME_LABEL = "NOME PARLATO:"
    ABOUT_THIS_ITEM_LABEL = "Informazioni su questo articolo"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODOTTI TESTATI"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "MIGLIORI"
    THUMBNAIL_PRICE_FROM = "da"
    THUMBNAIL_INSTEAD_OF = "invece di"
    THUMBNAIL_BEST_PRICE = "MIGLIOR PREZZO"
    THUMBNAIL_REVIEW_COUNT = "+100 Testati"
    THUMBNAIL_BEFORE_TEXT = "PRIMA"
    THUMBNAIL_AFTER_TEXT = "DOPO"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Le scorte cambiano velocemente — controlla i link qui sotto per la disponibilità attuale."
    OVERLAY_CTA_BANNER_TEXT = "LINK SOTTO PER IL MIGLIOR PREZZO"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "Allora, qual è il miglior {keyword} per te? Ecco il nostro verdetto finale."
    OUTRO_BEST_OVERALL = "Per le massime prestazioni e risultati professionali, la nostra scelta numero uno è senza dubbio il {top_choice_title}."
    OUTRO_BEST_VALUE = "Ma se cerchi il miglior rapporto qualità-prezzo, il campione è il {best_value_title}. È una scelta intelligente per un budget controllato."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "E incredibilmente, è anche il miglior rapporto qualità-prezzo che abbiamo trovato!"
    OUTRO_CALL_TO_ACTION = "I link a questi due campioni e a tutti gli altri {keyword} testati oggi si trovano qui sotto. Grazie per aver guardato, non dimenticare di iscriverti per altri confronti e alla prossima!"
    OUTRO_FALLBACK = "Puoi trovare i link a tutti i prodotti nella descrizione. Grazie per aver guardato e a presto!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Regola Speciale: Inizia il tuo SCRIPT con un'introduzione potente per il video. Menziona che per stabilire questa 'top 3 dei migliori {keyword}', il nostro team ha analizzato oltre 50 modelli. Quindi, presenta il prodotto attuale."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Regola Speciale: Termina il tuo SCRIPT con un invito all'azione menzionando che utilizzando i link nella descrizione, potrebbe essere applicato uno sconto speciale (ad es. 'Piccolo consiglio: utilizzando i link nella descrizione per aggiungere un prodotto al carrello, viene spesso applicato uno sconto a sorpresa!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Regola Speciale: Inizia il tuo SCRIPT introducendo questo prodotto come il primo in classifica, la scelta finale (ad es. 'E infine, in cima alla nostra classifica...' o 'Per coronare la nostra selezione...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} Migliori {keyword} del 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Trova i migliori {keyword} testati in questo video 👇"
    YOUTUBE_PRODUCT_LINE = "N°{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Disclaimer: Questo video e la descrizione contengono link di affiliazione, il che significa che se clicchi su uno dei link dei prodotti, riceverò una piccola commissione. Questo aiuta a sostenere il canale e ci permette di continuare a fare video come questo. Grazie per il supporto!"
    YOUTUBE_PINNED_COMMENT = "👇 Trova i migliori {keyword} testati in questo video 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "PRIMA"
    THUMBNAIL_AFTER_TEXT = "DOPO"
    THUMBNAIL_URGENCY_TEXT = "NUOVO 2025"
    THUMBNAIL_LIMITED_TEXT = "LIMITATO"
    THUMBNAIL_DISCOUNT_TEXT = "RISPARMIA €{amount}!"
    THUMBNAIL_PERCENT_OFF = "{percent}% SCONTO!"
    THUMBNAIL_TODAY_ONLY = "SOLO OGGI"

# To be used in scripts
Config = LanguageConfig()