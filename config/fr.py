from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'fr'
    VOICE_LANGUAGE = 'fr'
    TTS_LANGUAGE_CODE = 'fr-FR'
    
    # Amazon Scraping Settings
    AMAZON_TLD = 'fr'
    AMAZON_TAG = 'clickclickh01-21' # Replace with your French Amazon Associates tag if different

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Dis le texte suivant de manière naturelle, claire et engageante.'

    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "TITRE D'AFFICHAGE:"
    SPOKEN_NAME_LABEL = "NOM ORAL:"
    ABOUT_THIS_ITEM_LABEL = "À propos de cet article"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUITS TESTÉS"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "MEILLEURS"
    THUMBNAIL_PRICE_FROM = "à partir de"
    THUMBNAIL_INSTEAD_OF = "au lieu de"
    THUMBNAIL_BEST_PRICE = "MEILLEUR PRIX"
    THUMBNAIL_REVIEW_COUNT = "+100 Testés"
    THUMBNAIL_BEFORE_TEXT = "AVANT"
    THUMBNAIL_AFTER_TEXT = "APRÈS"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "Le stock évolue vite — consultez les liens ci‑dessous pour la disponibilité actuelle."
    OVERLAY_CTA_BANNER_TEXT = "LIEN CI-DESSOUS POUR LE MEILLEUR PRIX"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "Alors, quel est le meilleur {keyword} pour vous ? Voici notre verdict final."
    OUTRO_BEST_OVERALL = "Pour des performances maximales et des résultats professionnels, notre choix numéro un est sans conteste le {top_choice_title}."
    OUTRO_BEST_VALUE = "Mais si vous cherchez le meilleur rapport qualité-prix, le champion est le {best_value_title}. C'est un choix intelligent pour un budget maîtrisé."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "Et incroyablement, c'est aussi le meilleur rapport qualité-prix que nous ayons trouvé !"
    OUTRO_CALL_TO_ACTION = "Les liens vers ces deux champions et tous les autres {keyword} testés aujourd'hui se trouvent juste en dessous. Merci d'avoir regardé, n'oubliez pas de vous abonner pour plus de comparatifs et à la prochaine !"
    OUTRO_FALLBACK = "Vous pouvez retrouver les liens vers tous les produits dans la description. Merci d'avoir regardé et à bientôt !"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Règle Spéciale : Commence ton SCRIPT par une introduction percutante pour la vidéo. Mentionne que pour établir ce 'top 3 des meilleurs {keyword}', notre équipe a analysé plus de 50 modèles. Ensuite, introduis le produit actuel."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Règle Spéciale : Termine ton SCRIPT par un appel à l'action mentionnant qu'en utilisant les liens en description, une réduction spéciale pourrait s'appliquer. (par exemple : 'Petite astuce : en passant par les liens en description pour ajouter un produit au panier, une réduction surprise est souvent appliquée !')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Règle Spéciale : Commencez votre SCRIPT en présentant ce produit comme le numéro un du classement, le choix final (ex : 'Et enfin, au sommet de notre classement...' ou 'Pour couronner notre sélection...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} des Meilleurs {keyword} en 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Retrouvez les meilleurs {keyword} testés dans cette vidéo 👇"
    YOUTUBE_PRODUCT_LINE = "N°{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Clause de non-responsabilité : Cette vidéo et cette description contiennent des liens d'affiliation, ce qui signifie que si vous cliquez sur l'un des liens de produits, je recevrai une petite commission. Cela contribue à soutenir la chaîne et nous permet de continuer à faire des vidéos comme celle-ci. Merci pour votre soutien!"
    YOUTUBE_PINNED_COMMENT = "👇 Retrouvez les meilleurs {keyword} testés dans cette vidéo 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "AVANT"
    THUMBNAIL_AFTER_TEXT = "APRÈS"
    THUMBNAIL_URGENCY_TEXT = "NOUVEAU 2025"
    THUMBNAIL_LIMITED_TEXT = "LIMITÉ"
    THUMBNAIL_DISCOUNT_TEXT = "ÉCONOMIE €{amount}!"
    THUMBNAIL_PERCENT_OFF = "{percent}% RÉDUCTION!"
    THUMBNAIL_TODAY_ONLY = "AUJOURD'HUI SEULEMENT"

# To be used in scripts
Config = LanguageConfig() 