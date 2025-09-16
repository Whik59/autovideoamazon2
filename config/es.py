from .base import Config

class LanguageConfig(Config):
    # Language Settings
    CONTENT_LANGUAGE = 'es'
    VOICE_LANGUAGE = 'es'
    TTS_LANGUAGE_CODE = 'es-ES'

    # Amazon Scraping Settings
    AMAZON_TLD = 'es'
    AMAZON_TAG = 'clickclickh02-21'

    # Gemini TTS Settings
    GEMINI_TTS_PROMPT = 'Di el siguiente texto de forma natural, clara y atractiva.'
    
    # --- NEW: Labels for AI content parsing ---
    DISPLAY_TITLE_LABEL = "TÍTULO DE VISUALIZACIÓN:"
    SPOKEN_NAME_LABEL = "NOMBRE HABLADO:"
    ABOUT_THIS_ITEM_LABEL = "Acerca de este producto"

    # --- Thumbnail Text ---
    THUMBNAIL_SUBTITLE = "+100 PRODUCTOS PROBADOS"
    THUMBNAIL_TOP_TEXT = "TOP"
    THUMBNAIL_BEST_TEXT = "MEJORES"
    THUMBNAIL_PRICE_FROM = "desde"
    THUMBNAIL_INSTEAD_OF = "en lugar de"
    THUMBNAIL_BEST_PRICE = "MEJOR PRECIO"
    THUMBNAIL_REVIEW_COUNT = "+100 Probados"
    THUMBNAIL_BEFORE_TEXT = "ANTES"
    THUMBNAIL_AFTER_TEXT = "DESPUÉS"

    # --- NEW: Overlay Text ---
    OVERLAY_INFO_BANNER_TEXT = "El stock cambia rápido — consulta los enlaces de abajo para ver la disponibilidad actual."
    OVERLAY_CTA_BANNER_TEXT = "ENLACE ABAJO PARA EL MEJOR PRECIO"

    # --- NEW: Outro Text Templates ---
    OUTRO_LEAD_IN = "¿Entonces, cuál es el mejor {keyword} para ti? Aquí está nuestro veredicto final."
    OUTRO_BEST_OVERALL = "Para un rendimiento máximo y resultados profesionales, nuestra elección número uno es, sin duda, el {top_choice_title}."
    OUTRO_BEST_VALUE = "Pero si buscas la mejor relación calidad-precio, el campeón es el {best_value_title}. Es una elección inteligente para un presupuesto controlado."
    OUTRO_BEST_VALUE_IS_TOP_CHOICE = "¡E increíblemente, también es la mejor relación calidad-precio que hemos encontrado!"
    OUTRO_CALL_TO_ACTION = "Los enlaces a estos dos campeones y a todos los demás {keyword} probados hoy se encuentran justo debajo. Gracias por vernos, no olvides suscribirte para más comparativas, ¡y hasta la próxima!"
    OUTRO_FALLBACK = "Puedes encontrar los enlaces a todos los productos en la descripción. ¡Gracias por vernos y hasta pronto!"

    # --- NEW: Special Instructions for Scripts ---
    SPECIAL_INSTRUCTIONS_POSITION_5 = "\n- Regla Especial: Comienza tu GUIÓN con una introducción potente para el vídeo. Menciona que para establecer este 'top 3 de los mejores {keyword}', nuestro equipo analizó más de 50 modelos. Luego, presenta el producto actual."
    SPECIAL_INSTRUCTIONS_POSITION_3 = "\n- Regla Especial: Termina tu GUIÓN con una llamada a la acción mencionando que al usar los enlaces en la descripción, se podría aplicar un descuento especial (ej: 'Pequeño truco: al pasar por los enlaces de la descripción para añadir un producto a la cesta, ¡a menudo se aplica un descuento sorpresa!')."
    SPECIAL_INSTRUCTIONS_POSITION_1 = "\n- Regla Especial: Comienza tu GUIÓN presentando este producto como el número uno del ranking, la elección final (ej: 'Y finalmente, en la cima de nuestra clasificación...' o 'Para coronar nuestra selección...')."

    # --- NEW: YouTube Description ---
    YOUTUBE_TITLE = "Top {product_count} Mejores {keyword} de 2025"
    YOUTUBE_DESCRIPTION_LEAD_IN = "👇 Encuentra los mejores {keyword} probados en este video 👇"
    YOUTUBE_PRODUCT_LINE = "N°{position}: ({price}) 👉 {link}"
    YOUTUBE_DISCLAIMER = "Aviso legal: Este video y su descripción contienen enlaces de afiliado, lo que significa que si haces clic en uno de los enlaces de productos, recibiré una pequeña comisión. Esto ayuda a mantener el canal y nos permite seguir haciendo videos como este. ¡Gracias por tu apoyo!"
    YOUTUBE_PINNED_COMMENT = "👇 Encuentra los mejores {keyword} probados en este video 👇\n\n"
    YOUTUBE_INTRO_CHAPTER = "Intro"
    
    # Thumbnail translations
    THUMBNAIL_BEFORE_TEXT = "ANTES"
    THUMBNAIL_AFTER_TEXT = "DESPUÉS"
    THUMBNAIL_URGENCY_TEXT = "NUEVO 2025"
    THUMBNAIL_LIMITED_TEXT = "LIMITADO"
    THUMBNAIL_DISCOUNT_TEXT = "¡AHORRA €{amount}!"
    THUMBNAIL_PERCENT_OFF = "¡{percent}% DESCUENTO!"
    THUMBNAIL_TODAY_ONLY = "SOLO HOY"

# To be used in scripts
Config = LanguageConfig()