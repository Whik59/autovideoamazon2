from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'pl'
    VOICE_LANGUAGE = 'pl'
    TTS_LANGUAGE_CODE = 'pl-PL'

    # Amazon Scraping Settings
    AMAZON_TLD = 'pl'
    AMAZON_TAG = 'clickclickh06-21'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Powiedz następujący tekst w naturalny, wyraźny i angażujący sposób.'

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "TYTUŁ WYŚWIETLANY:"
    SPOKEN_NAME_LABEL = "NAZWA MÓWIONA:"
    ABOUT_THIS_ITEM_LABEL = "O tym produkcie"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUKTÓW PRZETESTOWANYCH"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "NAJLEPSZE"
    THUMBNAIL_PRICE_FROM = "od"
    THUMBNAIL_INSTEAD_OF = "zamiast"
    THUMBNAIL_BEST_PRICE = "NAJLEPSZA CENA"
    THUMBNAIL_REVIEW_COUNT = "+100 Przetestowanych"
    THUMBNAIL_BEFORE_TEXT = "PRZED"
    THUMBNAIL_AFTER_TEXT = "PO"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Stan magazynowy szybko się zmienia — sprawdź linki poniżej, aby zobaczyć aktualną dostępność."
    OVERLAY_CTA_BANNER_TEXT = "DODAJ DO KOSZYKA, JEŚLI JEST DOSTĘPNY"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "Więc, jaki jest najlepszy {keyword} dla Ciebie? Oto nasz ostateczny werdykt."
    OUTRO_BEST_OVERALL = "Dla maksymalnej wydajności i profesjonalnych rezultatów, nasz wybór numer jeden to bezapelacyjnie {top_choice_title}."
    OUTRO_BEST_VALUE = "Ale jeśli szukasz najlepszego stosunku jakości do ceny, mistrzem jest {best_value_title}. To mądry wybór przy ograniczonym budżecie."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "I co niewiarygodne, to także najlepszy stosunek jakości do ceny, jaki znaleźliśmy!"
    OUTRO_CALL_TO_ACTION = "Linki do tych dwóch mistrzów i wszystkich innych testowanych dzisiaj {keyword} znajdują się poniżej. Dziękujemy za oglądanie, nie zapomnij zasubskrybować, aby zobaczyć więcej porównań, i do zobaczenia następnym razem!"
    OUTRO_FALLBACK = "Linki do wszystkich produktów znajdziesz w opisie. Dziękujemy za oglądanie i do zobaczenia wkrótce!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Zasada Specjalna: Rozpocznij swój SKRYPT od mocnego wprowadzenia do filmu. Wspomnij, że aby stworzyć ten 'top 3 najlepszych {keyword}', nasz zespół przeanalizował ponad 50 modeli. Następnie przedstaw aktualny produkt."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Zasada Specjalna: Zakończ swój SKRYPT wezwaniem do działania, wspominając, że korzystając z linków w opisie, można zastosować specjalną zniżkę (np. 'Mała wskazówka: korzystając z linków w opisie, aby dodać produkt do koszyka, często stosowana jest niespodzianka zniżkowa!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Zasada Specjalna: Rozpocznij swój SKRYPT od przedstawienia tego produktu jako czołówki rankingu, ostatecznego wyboru (np. 'I na koniec, na szczycie naszego rankingu...' lub 'Aby ukoronować nasz wybór...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} Najlepszych {keyword} w 2025 roku"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Znajdź najlepsze {keyword} przetestowane w tym filmie 👇"
    YOUTUBE_PRODUCT_LINE = "Nr {position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Zastrzeżenie: Ten film i opis zawierają linki partnerskie, co oznacza, że jeśli klikniesz w jeden z linków do produktów, otrzymam niewielką prowizję. Pomaga to wspierać kanał i pozwala nam kontynuować tworzenie takich filmów. Dziękujemy za wsparcie!"
    YOUTUBE_PINNED_COMMENT = "👇 Znajdź najlepsze {keyword} przetestowane w tym filmie 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Wstęp"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "PRZED"
    THUMBNAIL_AFTER_TEXT = "PO"
    THUMBNAIL_URGENCY_TEXT = "NOWY 2025"
    THUMBNAIL_LIMITED_TEXT = "OGRANICZONY"
    THUMBNAIL_DISCOUNT_TEXT = "OSZCZĘDŹ {amount}zł!"
    THUMBNAIL_PERCENT_OFF = "{percent}% ZNIŻKI!"
    THUMBNAIL_TODAY_ONLY = "TYLKO DZIŚ"

# To be used in scripts
Config = LanguageConfig()