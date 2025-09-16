"""
Step 2: AI Content Rewriter & Voice Generator
"""

import os
import json
import time
import glob
import re
import concurrent.futures
from google.cloud import texttospeech
from num2words import num2words

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from google import genai as new_genai
    from google.genai import types as genai_types
    import wave
    import base64
except ImportError:
    new_genai = None
    genai_types = None

class ContentGenerator:
    def __init__(self, config, gemini_api_key=None, channel_name=None):
        self.config = config
        self.channel_name = channel_name
        
        # Initialize Google Cloud TTS Client only if using gcloud provider
        self.tts_client = None
        if getattr(self.config, 'TTS_PROVIDER', 'gcloud') == 'gcloud':
            try:
                self.tts_client = texttospeech.TextToSpeechClient()
                print("✅ Google Cloud Text-to-Speech client initialized.")
            except Exception as e:
                print(f"⚠️  Could not initialize Google Cloud TTS client: {e}")
                print("   Make sure you have set up Application Default Credentials or use gemini-tts instead.")
        else:
            print("✅ Skipping Google Cloud TTS client initialization (using gemini-tts provider).")

        # Announce TTS provider mode
        if getattr(self.config, 'TTS_PROVIDER', 'gcloud') == 'gemini-tts':
            print(f"✅ Gemini-TTS mode ON (model: {getattr(self.config, 'GEMINI_TTS_MODEL', 'gemini-2.5-flash-preview-tts')}, voice: {getattr(self.config, 'GEMINI_TTS_VOICE', 'Sulafat')}, lang: {getattr(self.config, 'TTS_LANGUAGE_CODE', 'fr-FR')})")
        else:
            print("✅ Standard Google Cloud TTS mode ON (non-Gemini model).")

        # Initialize Gemini AI for text generation
        self.gemini_flash_model = None
        self.gemini_pro_model = None
        
        # --- NEW: Setup API key rotation ---
        self.available_api_keys = getattr(self.config, 'GEMINI_API_KEYS', [])
        if gemini_api_key:
            # If a specific key was provided, add it to the front of the list
            if gemini_api_key not in self.available_api_keys:
                self.available_api_keys.insert(0, gemini_api_key)
        
        # Filter out placeholder keys
        self.available_api_keys = [k for k in self.available_api_keys if k and "YOUR" not in k]
        self.current_key_index = 0
        
        print(f"📊 Found {len(self.available_api_keys)} API keys for rotation")
        
        # Initialize with first available key
        if self.available_api_keys:
            self._initialize_gemini_clients(self.available_api_keys[0])
        else:
            print("⚠️ No valid Gemini API keys found. Script will use scraped descriptions directly.")
            self.gemini_tts_client = None
        
        os.makedirs(self.config.AUDIO_DIR, exist_ok=True)
    
    def _initialize_gemini_clients(self, api_key):
        """Initialize Gemini clients with a specific API key."""
        try:
            if genai:
                genai.configure(api_key=api_key)
                self.gemini_flash_model = genai.GenerativeModel('gemini-2.5-flash')
                self.gemini_pro_model = genai.GenerativeModel('gemini-1.5-pro')
                print(f"✅ Gemini Flash & Pro initialized with key {api_key[:20]}...")
            
            if new_genai:
                self.gemini_tts_client = new_genai.Client(api_key=api_key)
                print(f"✅ Gemini TTS client initialized with key {api_key[:20]}...")
                
        except Exception as e:
            print(f"⚠️ Could not initialize Gemini clients: {e}")
            self.gemini_tts_client = None
    
    def _is_quota_exhausted_error(self, error_str):
        """Check if the error indicates quota exhaustion."""
        quota_indicators = [
            "429 RESOURCE_EXHAUSTED",
            "You exceeded your current quota",
            "GenerateRequestsPerDayPerProjectPerModel",
            "quota"
        ]
        error_lower = str(error_str).lower()
        return any(indicator.lower() in error_lower for indicator in quota_indicators)
    
    def _rotate_to_next_api_key(self):
        """Rotate to the next available API key."""
        if len(self.available_api_keys) <= 1:
            print("❌ No more API keys available for rotation!")
            return False
        
        # Try each remaining key (don't go back to exhausted ones)
        original_index = self.current_key_index
        for _ in range(len(self.available_api_keys) - 1):
            self.current_key_index = (self.current_key_index + 1) % len(self.available_api_keys)
            next_key = self.available_api_keys[self.current_key_index]
            
            print(f"🔄 Trying API key {self.current_key_index + 1}/{len(self.available_api_keys)}: {next_key[:20]}...")
            self._initialize_gemini_clients(next_key)
            return True
        
        print("❌ All API keys have been tried!")
        return False

    def _save_pcm_as_wav(self, filepath, pcm_data, channels=1, sample_width=2, framerate=24000):
        """Saves raw PCM data to a WAV file."""
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(framerate)
            wf.writeframes(pcm_data)
        print(f"  ✅ Saved PCM data as WAV: {filepath}")

    def _is_quota_exhausted_error(self, error_str):
        """Checks if the error message indicates a quota exhaustion."""
        quota_indicators = [
            "429 RESOURCE_EXHAUSTED",
            "You exceeded your current quota",
            "GenerateRequestsPerDayPerProjectPerModel",
            "quota"
        ]
        error_lower = str(error_str).lower()
        return any(indicator.lower() in error_lower for indicator in quota_indicators)
    
    def _number_to_word(self, number, language):
        """Convert a number to its written form in the specified language."""
        number_words = {
            'de': {1: 'eins', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf'},
            'en': {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'},
            'es': {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco'},
            'fr': {1: 'un', 2: 'deux', 3: 'trois', 4: 'quatre', 5: 'cinq'},
            'it': {1: 'uno', 2: 'due', 3: 'tre', 4: 'quattro', 5: 'cinque'},
            'nl': {1: 'een', 2: 'twee', 3: 'drie', 4: 'vier', 5: 'vijf'},
            'pl': {1: 'jeden', 2: 'dwa', 3: 'trzy', 4: 'cztery', 5: 'pięć'},
            'sv': {1: 'ett', 2: 'två', 3: 'tre', 4: 'fyra', 5: 'fem'}
        }
        
        # Get the word for the number in the specified language
        if language in number_words and number in number_words[language]:
            return number_words[language][number]
        else:
            # Fallback to the number if language or number not found
            return str(number)

    def _clean_text_for_tts(self, text):
        """Clean text for TTS by removing unwanted punctuation and formatting."""
        # Remove backslashes and escape characters
        text = text.replace('\\', '')
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove *italic*
        text = re.sub(r'__(.*?)__', r'\1', text)      # Remove __underline__
        text = re.sub(r'_(.*?)_', r'\1', text)        # Remove _underscore_
        
        # Remove special characters but keep basic punctuation
        # Keep: . ! ? , ; : ( ) - ' spaces and letters/numbers
        text = re.sub(r"[^\w\s.!?,:;()\-àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ']", '', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up spaces before punctuation
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        
        return text.strip()

    def _strip_position_three_intro(self, text, position, language):
        """Remove any global 'Top 3' style intro from non-first segments (positions other than 3).
        This guards against LLM occasionally adding an intro despite prompt constraints.
        """
        if not text or position == 3:
            return text
        # Remove a leading sentence mentioning Top 3/Top three in a language-agnostic way
        # Only strip if it appears at the very beginning to avoid removing legitimate content later
        pattern = r"(?is)^\s*[^.]*\btop\s*3\b[^.]*\.\s*"
        cleaned = re.sub(pattern, '', text)
        return cleaned.strip()

    def _generate_with_gemini(self, prompt, retries=5, model='flash'):
        """Generates content using a specific Gemini model with retries."""
        
        selected_model = self.gemini_flash_model if model == 'flash' else self.gemini_pro_model

        if not selected_model:
            print(f"  ⚠️ Gemini model '{model}' not available.")
            return None
        
        for attempt in range(retries):
            try:
                response = selected_model.generate_content(prompt)
                if response.candidates and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text.strip()
            except Exception as e:
                print(f"  ⚠️ Gemini '{model}' model error (attempt {attempt + 1}/{retries}): {str(e)[:100]}...")
                if attempt < retries - 1:
                    sleep_time = 2 ** attempt
                    print(f"     Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
        
        print(f"  ❌ Gemini '{model}' model generation failed after {retries} attempts.")
        return None

    def _rewrite_title(self, product_data):
        """
        Uses Gemini AI to rewrite the product title to be short and catchy for display,
        and also generates a very short "spoken name" for use in narration.
        Returns a tuple: (short_title, spoken_name)
        """
        original_title = product_data.get('title', '')
        if not self.gemini_flash_model:
            return original_title, original_title # Fallback if AI is not available

        description_text = " ".join(product_data.get('description', []))

        try:
            prompt_filename = f'prompts/short_title_prompt_{self.config.CONTENT_LANGUAGE}.txt'
            with open(prompt_filename, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            prompt = prompt_template.format(
                product_title=original_title,
                description_text=description_text
            )
        except FileNotFoundError:
            print(f"  ❌ Error: {prompt_filename} not found.")
            return original_title, original_title
        except Exception as e:
            print(f"  ❌ Error reading or formatting title prompt: {e}")
            return original_title, original_title

        response_text = self._generate_with_gemini(prompt, model='flash')

        if not response_text:
            print(f"  ⚠️ AI title generation failed. Using original title.")
            return original_title, original_title

        # Parse the response to get both the display title and the spoken name
        # Use the language-specific labels from the config file to build the regex
        display_title_regex = re.escape(self.config.DISPLAY_TITLE_LABEL)
        spoken_name_regex = re.escape(self.config.SPOKEN_NAME_LABEL)

        short_title_match = re.search(f"^{display_title_regex}\\s*(.*)", response_text, re.IGNORECASE | re.MULTILINE)
        spoken_name_match = re.search(f"^{spoken_name_regex}\\s*(.*)", response_text, re.IGNORECASE | re.MULTILINE)

        short_title = short_title_match.group(1).strip() if short_title_match else original_title
        spoken_name = spoken_name_match.group(1).strip() if spoken_name_match else short_title.split()[0] # Fallback to first word of title

        # --- NEW: Stricter enforcement of title length ---
        if len(short_title.split()) > 5:
            print(f"  ⚠️ AI generated a long title ('{short_title}'). Truncating to 5 words.")
            short_title = " ".join(short_title.split()[:5])

        if len(spoken_name.split()) > 3:
            print(f"  ⚠️ AI generated a long spoken name ('{spoken_name}'). Truncating to 3 words.")
            spoken_name = " ".join(spoken_name.split()[:3])

        print(f"  ✅ AI titles generated: '{short_title}' / '{spoken_name}'")
        return short_title, spoken_name

    def _get_position_two_cta(self, language):
        """Return a compliant teaser CTA for position #2, hinting #1 is in high demand."""
        ctas = {
            'en': "Before we reveal number one: featured items often sell out fast. Check the links below for current availability and, if it's in stock, add it to your cart to hold it.",
            'fr': "Avant de passer au numéro un : les produits présentés partent vite et peuvent être en rupture. Cliquez sur les liens sous la vidéo pour vérifier la disponibilité et, si c’est dispo, ajoutez‑le au panier pour le garder de côté.",
            'es': "Antes de revelar el número uno: los productos presentados suelen agotarse rápido. Revisa los enlaces debajo del vídeo para ver la disponibilidad actual y, si está disponible, añádelo al carrito para reservarlo.",
            'de': "Bevor wir die Nummer eins zeigen: Die vorgestellten Produkte sind oft schnell ausverkauft. Prüfe die Links unter dem Video für die aktuelle Verfügbarkeit und lege den Artikel, falls verfügbar, in den Warenkorb, um ihn zu sichern.",
            'it': "Prima di svelare il numero uno: i prodotti presentati si esauriscono spesso in fretta. Controlla i link sotto al video per la disponibilità aggiornata e, se è disponibile, aggiungilo al carrello per tenerlo da parte.",
            'nl': "Voordat we nummer één onthullen: de getoonde producten raken vaak snel uitverkocht. Check de links onder de video voor de actuele beschikbaarheid en voeg het, als het beschikbaar is, toe aan je winkelwagen om het te bewaren.",
            'pl': "Zanim przejdziemy do numeru jeden: prezentowane produkty często szybko się wyprzedają. Sprawdź linki pod filmem, a jeśli produkt jest dostępny, dodaj go do koszyka, aby go zachować.",
            'sv': "Innan vi avslöjar nummer ett: produkterna vi visar tar ofta slut snabbt. Kolla länkarna under videon för aktuell tillgänglighet och lägg den i varukorgen om den finns i lager för att spara den.",
        }
        return ctas.get(language, ctas['en'])

    def _generate_product_script(self, task_data):
        """Generates a persuasive script for a single product."""
        product, keyword, previous_product = task_data
        
        if not self.gemini_flash_model:
            return ""

        try:
            prompt_filename = f'prompts/script_prompt_{self.config.CONTENT_LANGUAGE}.txt'
            with open(prompt_filename, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            position = product.get('position')
            # Convert position number to words in the appropriate language
            position_word = self._number_to_word(position, self.config.CONTENT_LANGUAGE)

            prompt = prompt_template.format(
                position=position_word,
                previous_spoken_name=previous_product.get('spoken_name', '') if previous_product else '',
                keyword=keyword,
                spoken_name=product.get('spoken_name', ''),
                current_product_title=product.get('title', ''),
                current_product_description=" ".join(product.get('description', []))
            )
        except FileNotFoundError:
            print(f"  ❌ Error: {prompt_filename} not found.")
            return ""
        except Exception as e:
            print(f"  ❌ Error reading or formatting the script prompt: {e}")
            return ""

        script = self._generate_with_gemini(prompt, model='flash')
        print(f"  ✅ Generated script for product #{product.get('position')}")
        cleaned = self._clean_text_for_tts(script)
        cleaned = self._strip_position_three_intro(cleaned, product.get('position'), self.config.CONTENT_LANGUAGE)
        if product.get('position') == 2:
            cta = self._get_position_two_cta(self.config.CONTENT_LANGUAGE)
            cleaned = f"{cleaned} {cta}".strip()
        return cleaned

    def _generate_hero_outro(self, products, keyword):
        """
        Generates a dynamic, AI-powered outro recommending the "best overall" product.
        """
        if not self.gemini_pro_model:
            print("  ⚠️ Gemini Pro model not available for outro generation. Skipping.")
            return ""

        top_choice = next((p for p in products if p.get('position') == 1), None)
        
        if not top_choice:
            print("  ⚠️ Could not determine top choice product. Skipping outro.")
            return ""

        top_choice_name = top_choice.get('spoken_name', top_choice.get('short_title', ''))

        try:
            prompt_filename = f'prompts/outro_prompt_{self.config.CONTENT_LANGUAGE}.txt'
            with open(prompt_filename, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            prompt = prompt_template.format(
                keyword=keyword,
                top_choice_name=top_choice_name
            )
        except FileNotFoundError:
            print(f"  ❌ Error: {prompt_filename} not found.")
            return ""
        except Exception as e:
            print(f"  ❌ Error reading or formatting the outro prompt: {e}")
            return ""

        outro_script = self._generate_with_gemini(prompt, model='pro')
        
        if not outro_script:
            print("  ⚠️ AI outro generation failed.")
            return ""
            
        print("  ✅ AI-generated 'Hero' outro script.")
        return self._clean_text_for_tts(outro_script)

    def _generate_audio(self, text, filename, voice_name, prompt=None):
        """Generates audio file for the given text using the Google Cloud TTS API.
        The voice_name is now dynamically passed in.
        """
        filepath = os.path.join(self.config.AUDIO_DIR, filename)
        
        # Choose provider
        provider = getattr(self.config, 'TTS_PROVIDER', 'gcloud')
        use_gemini_tts = (provider == 'gemini-tts')

        speaking_rate = getattr(self.config, 'TTS_SPEAKING_RATE', 1.0)
        is_ssml = "ssml" in filename.lower() # A simple check based on filename convention

        try:
            print(f"  🎙️ Generating audio for: {filename} (Voice: {voice_name})")

            if use_gemini_tts and self.gemini_tts_client:
                try:
                    # Use the new Gemini TTS API
                    tts_prompt = prompt or getattr(self.config, 'GEMINI_TTS_PROMPT', 'Say the following.')
                    model_name = getattr(self.config, 'GEMINI_TTS_MODEL', 'gemini-2.5-flash-preview-tts')
                    
                    # Prepare the full prompt
                    full_prompt = f"{tts_prompt}\n\n{text}"
                    
                    # Generate content with TTS
                    response = self.gemini_tts_client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                        config=genai_types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=genai_types.SpeechConfig(
                                voice_config=genai_types.VoiceConfig(
                                    prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                                        voice_name=voice_name, # Use the dynamically passed voice name
                                    )
                                )
                            ),
                        )
                    )
                    
                    # Extract audio data (it's already raw PCM bytes)
                    if response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content.parts:
                            audio_part = candidate.content.parts[0]
                            if hasattr(audio_part, 'inline_data') and audio_part.inline_data.data:
                                pcm_data = audio_part.inline_data.data
                                
                                # Save as WAV 
                                wav_filepath = filepath.replace('.mp3', '.wav')
                                self._save_pcm_as_wav(wav_filepath, pcm_data)
                                print(f"  ✅ Gemini TTS audio generated successfully: {filename}")
                                return wav_filepath
                            elif hasattr(audio_part, 'text'):
                                print(f"  ⚠️ Received text instead of audio: {audio_part.text}")
                        
                        # If we reach here, something was wrong with the response structure
                        print("  ⚠️ No valid audio data found in Gemini TTS response. Falling back to standard TTS.")
                        use_gemini_tts = False
                    else:
                        print("  ⚠️ No candidates in Gemini TTS response. Falling back to standard TTS.")
                        use_gemini_tts = False
                        
                except Exception as e:
                    error_str = str(e)
                    print(f"  ⚠️ Gemini-TTS synthesis failed: {error_str}")
                    
                    # Check if this is a quota exhaustion error
                    if self._is_quota_exhausted_error(error_str):
                        print("  🔄 Quota exhausted! Attempting to rotate to next API key...")
                        if self._rotate_to_next_api_key():
                            print("  🔄 Retrying with new API key...")
                            # Retry with the new key
                            try:
                                response = self.gemini_tts_client.models.generate_content(
                                    model=model_name,
                                    contents=full_prompt,
                                    config=genai_types.GenerateContentConfig(
                                        response_modalities=["AUDIO"],
                                        speech_config=genai_types.SpeechConfig(
                                            voice_config=genai_types.VoiceConfig(
                                                prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                                                    voice_name=voice_name,
                                                )
                                            )
                                        ),
                                    )
                                )
                                print("  ✅ Retry successful with rotated API key!")
                                # Continue with the successful response...
                                if response.candidates:
                                    candidate = response.candidates[0]
                                    if hasattr(candidate, 'content') and candidate.content.parts:
                                        audio_part = candidate.content.parts[0]
                                        if hasattr(audio_part, 'inline_data') and audio_part.inline_data.data:
                                            pcm_data = audio_part.inline_data.data
                                            
                                            # Save as WAV
                                            wav_filepath = filepath.replace('.mp3', '.wav')
                                            self._save_pcm_as_wav(wav_filepath, pcm_data)
                                            print(f"  ✅ Gemini TTS audio generated successfully after retry: {filename}")
                                            return wav_filepath
                                        
                                # If retry also fails to produce audio, fall back
                                print(f"  ❌ Retry failed to produce valid audio. Falling back to standard TTS.")
                                use_gemini_tts = False
                                
                            except Exception as retry_error:
                                retry_error_str = str(retry_error)
                                if self._is_quota_exhausted_error(retry_error_str):
                                    print(f"  ❌ Retry key also quota exhausted. Stopping pipeline to prevent mixed audio.")
                                    raise Exception("❌ ALL GEMINI API KEYS QUOTA EXHAUSTED! Pipeline stopped to prevent mixed audio quality. Please wait for quota reset or add more API keys.")
                                else:
                                    print(f"  ❌ Retry failed with different error: {retry_error}. Falling back to standard TTS.")
                                    use_gemini_tts = False
                        else:
                            print("  ❌ ALL API keys quota exhausted! Stopping pipeline to prevent mixed audio.")
                            raise Exception("❌ ALL GEMINI API KEYS QUOTA EXHAUSTED! Pipeline stopped to prevent mixed audio quality. Please wait for quota reset or add more API keys.")
                    else:
                        print(f"  ❌ Non-quota error: {error_str}. Falling back to standard TTS.")
                        use_gemini_tts = False
            elif use_gemini_tts and not self.gemini_tts_client:
                print("  ⚠️ Gemini TTS client not available. Falling back to standard TTS.")
                use_gemini_tts = False

            if not use_gemini_tts:
                # Check if Google Cloud TTS client is available
                if not self.tts_client:
                    raise Exception("❌ Neither Gemini TTS nor Google Cloud TTS is available. Please configure one of them.")
                
                # Use SSML if the text contains SSML tags, otherwise use plain text
                is_ssml = text.strip().startswith('<speak>')
                if is_ssml:
                    synthesis_input = texttospeech.SynthesisInput(ssml=text)
                else:
                    synthesis_input = texttospeech.SynthesisInput(text=text)
                
                # Use a standard, high-quality French voice by default.
                voice = texttospeech.VoiceSelectionParams(
                    language_code=getattr(self.config, 'TTS_LANGUAGE_CODE', 'fr-FR'),
                    name="fr-FR-Standard-A"
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speaking_rate
                )
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

            with open(filepath, "wb") as out:
                out.write(response.audio_content)

            print(f"  ✅ Audio generated successfully: {filename}")
            return filepath
            
        except Exception as e:
            print(f"  ❌ An unexpected error occurred generating audio for {filename}: {str(e)}")
            return None

    def _process_audio_task(self, task):
        """Helper function to be called in parallel for generating audio."""
        try:
            default_prompt = getattr(self.config, 'GEMINI_TTS_PROMPT', 'Say the following in a clear, natural and engaging way.')
            # --- MODIFIED: Use the voice assigned to the task ---
            voice_to_use = task.get('voice', 'Sulafat') # Default to Sulafat if not specified
            
            # --- MODIFIED: Expect a .wav file from Gemini TTS ---
            audio_path = self._generate_audio(task['text'], task['filename'], voice_to_use, prompt=default_prompt)
            
            if audio_path:
                task['audio_file'] = audio_path
            else:
                task['audio_file'] = None
                print(f"  -  Skipping audio assignment for {task['filename']} due to generation failure.")
            return task
        except Exception as exc:
            # Check if this is a quota exhaustion error - if so, re-raise to stop the pipeline
            if "ALL GEMINI API KEYS QUOTA EXHAUSTED" in str(exc):
                print(f"  ❌ Critical error: All Gemini API keys quota exhausted. Stopping pipeline.")
                raise exc  # Re-raise to stop the entire pipeline
            else:
                print(f"  ❌ Audio generation for {task['filename']} failed in thread: {exc}")
                task['audio_file'] = None
                return task

    def run(self, keyword=None, preview_only=False):
        """Main process to generate content and audio."""
        if preview_only:
            print("📝 STEP 2: PREVIEW MODE - Rewriting Content Only")
        else:
            print("📝 STEP 2: Rewriting Content & Generating Voice")
        print("=" * 50)
        
        # 1. Load Scraped Data
        scraped_file_path = os.path.join(self.config.OUTPUT_DIR, "product.json")
        if not os.path.exists(scraped_file_path):
            print(f"❌ Scraped file not found: {scraped_file_path}. Run Step 1 first.")
            return
        
        # If no keyword is provided, try to read it from channel-specific keywords file
        if not keyword and self.channel_name:
            keyword_file_path = os.path.join("keywords", self.config.CONTENT_LANGUAGE, f"{self.channel_name}.txt")
            if os.path.exists(keyword_file_path):
                with open(keyword_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            keyword = line.strip()
                            print(f"✅ Automatically detected keyword '{keyword}' from {keyword_file_path}.")
                            break
            else:
                # Fallback to old method if channel-specific file doesn't exist
                keywords_file = f'keywords_{self.config.CONTENT_LANGUAGE}.txt'
                if os.path.exists(keywords_file):
                    with open(keywords_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                keyword = line.strip()
                                print(f"✅ Automatically detected keyword '{keyword}' from {keywords_file}.")
                                break
        
        if not keyword:
            print(f"❌ Error: No keyword provided and no keyword file found for channel '{self.channel_name}'.")
            return

        with open(scraped_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        print(f"✅ Loaded {len(products)} products for '{keyword}' from '{os.path.basename(scraped_file_path)}'.")

        enhanced_data = {'keyword': keyword, 'products': []}
        
        # Sort products by original scraped order to ensure positions are correct (3 down to 1)
        products.sort(key=lambda p: p.get('index', 0))
        for i, product in enumerate(products):
            product['position'] = len(products) - i
        
        # --- START: Title Generation (Must be first) ---
        print(f"\n✍️  Generating display titles & spoken names for {len(products)} products (in parallel)...")
        start_time_titles = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            title_results = list(executor.map(self._rewrite_title, products))
        for i, product in enumerate(products):
            product['short_title'], product['spoken_name'] = title_results[i]
        end_time_titles = time.time()
        print(f"✅ AI title processing finished in {end_time_titles - start_time_titles:.2f} seconds.")

        # --- START: AI Content Generation (Now uses spoken names) ---
        print(f"\n✍️  Generating scripts for {len(products)} products (in parallel)...")
        start_time_scripts = time.time()
        
        # Create tasks with previous product context for transitions
        script_tasks = []
        for i, p in enumerate(products):
            previous_product = products[i-1] if i > 0 else None
            script_tasks.append((p, keyword, previous_product))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            scripts = list(executor.map(self._generate_product_script, script_tasks))
        for i, product in enumerate(products):
            product['script'] = scripts[i]
        end_time_scripts = time.time()
        print(f"✅ AI script processing finished in {end_time_scripts - start_time_scripts:.2f} seconds.")

        # --- END: AI Content Generation ---

        # --- START: Hero Outro Generation ---
        print("\n✍️  Generating 'Hero' outro...")
        hero_outro_script = self._generate_hero_outro(products, keyword)
        # Find product #1 and append the outro to its script
        product_one = next((p for p in products if p.get('position') == 1), None)
        if product_one:
            product_one['script'] = (product_one.get('script', '') + " " + hero_outro_script).strip()
            print("  ✅ 'Hero' outro appended to script for product #1.")
        # --- END: Hero Outro Generation ---

        # Add the fully processed products to our final data structure
        enhanced_data['products'] = products

        # 5. Generate all audio if not in preview mode
        if not preview_only:
            provider = getattr(self.config, 'TTS_PROVIDER', 'gcloud')
            tasks = []

            # --- MODIFIED: Use voice mapping to assign a voice to each audio task ---
            print("\n✅ Generating final audio tasks with voice mapping...")
            voice_mapping = getattr(self.config, 'GEMINI_TTS_VOICE_MAPPING', {})
            default_voice = voice_mapping.get('default', 'Sulafat') # Fallback voice

            for p in enhanced_data['products']:
                position = p['position']
                voice_for_product = voice_mapping.get(position, default_voice)
                print(f"   - Assigning voice '{voice_for_product}' to product #{position}")
                tasks.append({
                    'text': p['script'],
                    'filename': f"product_{p['position']}_audio.mp3",
                    'type': 'final_audio',
                    'position': p['position'],
                    'voice': voice_for_product  # Add the selected voice to the task
                })
            # --- END: Final Audio Task Generation ---

            start_time = time.time()

            # This part remains largely the same, but the logic to assign files back needs to be simplified
            try:
                if provider == 'gemini-tts':
                    print(f"\n🎙️  Generating {len(tasks)} final audio files with Gemini TTS (in parallel bursts)...")
                    
                    # Process tasks in chunks to respect the 10 RPM limit
                    chunk_size = 10
                    for i in range(0, len(tasks), chunk_size):
                        chunk = tasks[i:i + chunk_size]
                        print(f"--- Processing audio chunk {i//chunk_size + 1} ({len(chunk)} tasks) ---")
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=chunk_size) as executor:
                            future_to_task = {executor.submit(self._process_audio_task, task): task for task in chunk}
                            
                            for future in concurrent.futures.as_completed(future_to_task):
                                result_task = future.result()
                                if not result_task or not result_task.get('audio_file'):
                                    continue
                                
                                product_to_update = next((p for p in enhanced_data['products'] if p['position'] == result_task['position']), None)
                                if product_to_update:
                                    product_to_update['final_audio_file'] = result_task['audio_file']

                        if i + chunk_size < len(tasks):
                            print("  ⏳ Waiting 61 seconds for RPM quota to reset...")
                            time.sleep(61)
                
                else: # Fallback for standard gcloud TTS
                    print(f"\n🎙️  Generating {len(tasks)} audio files with Google Cloud TTS (in parallel)...")
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        future_to_task = {executor.submit(self._process_audio_task, task): task for task in tasks}
                        
                        for future in concurrent.futures.as_completed(future_to_task):
                            result_task = future.result()
                            if not result_task or not result_task.get('audio_file'):
                                continue
                            
                            product_to_update = next((p for p in enhanced_data['products'] if p['position'] == result_task['position']), None)
                            if product_to_update:
                                product_to_update['final_audio_file'] = result_task['audio_file']
            
            except Exception as e:
                # Check if this is a quota exhaustion error
                if "ALL GEMINI API KEYS QUOTA EXHAUSTED" in str(e):
                    print(f"\n❌ CRITICAL ERROR: All Gemini API keys quota exhausted!")
                    print("   - Pipeline stopped to prevent mixed audio quality.")
                    print("   - Please wait for quota reset or add more API keys.")
                    raise e  # Re-raise to stop the entire pipeline
                else:
                    print(f"\n❌ Unexpected error during audio processing: {e}")
                    raise e  # Re-raise any other critical errors

            end_time = time.time()
            print(f"✅ Audio processing finished in {end_time - start_time:.2f} seconds.")
        
        # 6. Save final data
        output_file = os.path.join(self.config.OUTPUT_DIR, "enhanced_product.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        if preview_only:
            print("\n" + "=" * 50)
            print("✅ Preview content generated. Audio was skipped.")
            print(f"   Review the JSON file: {output_file}")
        else:
            print("\n" + "=" * 50)
            print(f"🎉 Enhanced content saved to {output_file}")
            print("✅ Ready for Step 3: Video Assembly!")

if __name__ == "__main__":
    import argparse
    import sys
    from config import get_config

    parser = argparse.ArgumentParser(description="Standalone content and audio generator for a specific language.")
    parser.add_argument('language', type=str, help="The language code to use (e.g., 'es', 'de').")
    parser.add_argument('--keyword', type=str, default=None, help='(Optional) Keyword for the product category. If not provided, uses the first keyword from the channel-specific keywords file.')
    parser.add_argument('--channel', type=str, default=None, help='(Optional) Channel name to load keywords from keywords/{language}/{channel}.txt')
    parser.add_argument('--preview', action='store_true', help='Run in preview mode without generating audio.')
    # --- NEW: Argument to accept a specific API key ---
    parser.add_argument('--api-key', type=str, help='(Optional) Gemini API key to use for this run.')
    args = parser.parse_args()

    try:
        print(f"▶️  Running Step 2 in standalone mode for language '{args.language}'")
        Config = get_config(args.language)
        print(f"✅ Loaded configuration for language: {Config.CONTENT_LANGUAGE}")

        generator = ContentGenerator(Config, gemini_api_key=args.api_key, channel_name=args.channel)
        generator.run(keyword=args.keyword, preview_only=args.preview)

    except ImportError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1) 