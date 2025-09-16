import os
import sys
import base64
import wave
import time # <-- Added for rate limiting
from pydub import AudioSegment

try:
    from google import genai as new_genai
    from google.genai import types as genai_types
except ImportError:
    print("❌ ERROR: Required Gemini TTS libraries not found.")
    print("Please install: pip install google-genai")
    sys.exit(1)

# Import config to get API keys
try:
    from config import get_config
    Config = get_config('fr')  # Use French config for testing
except ImportError:
    print("❌ ERROR: Could not import config. Using hardcoded keys as fallback.")
    Config = None

def _save_pcm_as_wav(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    """Save raw PCM data as a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def _convert_wav_to_mp3(wav_filepath, mp3_filepath):
    """Convert WAV to MP3 using pydub."""
    try:
        audio = AudioSegment.from_wav(wav_filepath)
        audio.export(mp3_filepath, format="mp3", bitrate="128k")
        os.remove(wav_filepath)  # Clean up WAV file
        return True
    except Exception:
        return False

def _is_quota_exhausted_error(error_str):
    """Check if the error indicates quota exhaustion."""
    quota_indicators = [
        "429 RESOURCE_EXHAUSTED",
        "You exceeded your current quota",
        "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
        "quota"
    ]
    error_lower = str(error_str).lower()
    return any(indicator.lower() in error_lower for indicator in quota_indicators)

def test_gemini_tts_voice_with_rotation():
    """Test Gemini TTS with automatic API key rotation when quota is exhausted."""
    
    # Get API keys from config or use fallback
    if Config and hasattr(Config, 'GEMINI_API_KEYS'):
        api_keys = Config.GEMINI_API_KEYS
        print(f"✅ Loaded {len(api_keys)} API keys from config.")
    else:
        # Fallback keys
        api_keys = [
            "AIzaSyAyBxM9Q4OM3kXGefboDDz3D52vbPEjDPc",
            "AIzaSyAz-2QpjTB17-iJNVGZm1DRVO6HUmxV6rg",
            "AIzaSyBdYz04o9vVORDLQ56eDGwMEFpjccIGWtQ"
        ]
        print(f"⚠️  Using fallback API keys ({len(api_keys)} keys).")
    
    print("🎙️  GEMINI TTS VOICE TEST WITH KEY ROTATION")
    print("=" * 50)
    
    # French test samples - will be combined into a single request
    test_samples = [
        "Bienvenue à tous dans notre test complet des 5 meilleures machines de cuisine pour 2025. Dans cette vidéo, nous plongeons dans l'univers des mixeurs haute performance et des robots culinaires pour vous aider à trouver l'appareil parfait pour vos besoins culinaires.",
        
        "À la cinquième place, nous avons l'impressionnante KitchenAid Artisan. Ce modèle iconique n'est pas seulement un point fort visuel dans toute cuisine, mais convainc aussi par sa construction robuste entièrement métallique et sa durabilité exceptionnelle.",
        
        "D'un point de vue technique, le moteur fonctionne avec une transmission à entraînement direct, ce qui garantit une perte de puissance minimale entre le moteur et l'accessoire. Le boîtier offre une stabilité exceptionnelle et réduit les vibrations.",
        
        "En termes de rapport qualité-prix, cette machine offre une valeur exceptionnelle. La combinaison d'un moteur puissant, de matériaux de haute qualité et d'un design réfléchi justifie complètement l'investissement.",
        
        "En résumé, cette machine mérite sa place dans notre classement. Elle représente un excellent choix pour tous ceux qui prennent la cuisine au sérieux et recherchent un équipement de qualité professionnelle."
    ]
    
    # Create output directory
    os.makedirs("voice_test_output", exist_ok=True)
    
    # Combine all samples with pauses
    combined_text = ""
    for i, sample in enumerate(test_samples, 1):
        combined_text += f"Échantillon {i}: {sample}"
        if i < len(test_samples):
            combined_text += "\n\n... Pause de 2 secondes ...\n\n"
    
    print(f"Combining {len(test_samples)} text samples into 1 API call...")
    print(f"Total text length: {len(combined_text)} characters")
    print(f"Estimated tokens: ~{len(combined_text)//4}")
    print()
    
    # Try each API key until one works
    for key_index, api_key in enumerate(api_keys):
        print(f"🔑 Trying API key {key_index + 1}/{len(api_keys)}: {api_key[:20]}...")
        
        try:
            # Configure Gemini TTS client with current key
            gemini_tts_client = new_genai.Client(api_key=api_key)
            print("   ✅ Client initialized successfully.")
            
            # Create the TTS prompt - for French
            tts_prompt = "Dis le texte suivant de manière naturelle, claire et engageante. Fais une pause naturelle de 2 secondes quand tu vois 'Pause de 2 secondes'."
            
            # Prepare the full prompt
            full_prompt = f"{tts_prompt}\n\n{combined_text}"
            
            print("   🎙️ Making TTS API request...")
            
            # Generate audio using the EXACT same format as step2_content.py
            response = gemini_tts_client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=full_prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=genai_types.SpeechConfig(
                        voice_config=genai_types.VoiceConfig(
                            prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                                voice_name="Sulafat",
                            )
                        )
                    ),
                )
            )
            
            # Save the audio (using the exact same robust parsing as step2_content.py)
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and len(candidate.content.parts) > 0:
                    audio_part = candidate.content.parts[0]
                    if hasattr(audio_part, 'inline_data') and audio_part.inline_data:
                        pcm_data = audio_part.inline_data.data  # Do NOT base64 decode - use directly
                        
                        if len(pcm_data) == 0:
                            print("   ❌ ERROR: Received 0 bytes of audio data.")
                            continue  # Try next key
                        
                        # Save as WAV first using the exact method from step2_content.py
                        filename = f"combined_french_voice_test_key{key_index + 1}.mp3"
                        wav_path = os.path.join("voice_test_output", filename.replace('.mp3', '.wav'))
                        _save_pcm_as_wav(wav_path, pcm_data)
                        
                        # Convert to MP3 using the exact method from step2_content.py
                        mp3_path = os.path.join("voice_test_output", filename)
                        if _convert_wav_to_mp3(wav_path, mp3_path):
                            print(f"   ✅ SUCCESS: Saved to {mp3_path}")
                        else:
                            # Keep as WAV if conversion failed
                            os.rename(wav_path, mp3_path.replace('.mp3', '.wav'))
                            print(f"   ✅ SUCCESS: Saved to {mp3_path.replace('.mp3', '.wav')} (WAV format)")
                        
                        print("\n" + "=" * 50)
                        print(f"🎉 VOICE TEST COMPLETE WITH KEY {key_index + 1}!")
                        print(f"✅ Generated: 1/1 audio file successfully")
                        print(f"📁 Files saved in: voice_test_output/")
                        print(f"🔑 Working API key: {api_key[:20]}...")
                        
                        print(f"\n🎧 Listen to the generated file:")
                        print(f"   - {filename}")
                        print(f"   - Contains all 5 test samples with natural pauses")
                        
                        return True  # Success!
                    else:
                        print(f"   ❌ ERROR: No audio data found in the response part.")
                        continue  # Try next key
                else:
                    print(f"   ❌ ERROR: No content parts found in the response candidate.")
                    continue  # Try next key
            else:
                print(f"   ❌ ERROR: No candidates found in the API response.")
                continue  # Try next key
                
        except Exception as e:
            error_str = str(e)
            print(f"   ❌ ERROR: {error_str}")
            
            # Check if this is a quota exhaustion error
            if _is_quota_exhausted_error(error_str):
                print(f"   🔄 Quota exhausted for key {key_index + 1}. Trying next key...")
                continue  # Try next key
            else:
                print(f"   ⚠️  Non-quota error with key {key_index + 1}. Trying next key...")
                continue  # Try next key for any error
    
    # If we get here, all keys failed
    print("\n" + "=" * 50)
    print("❌ ALL API KEYS FAILED!")
    print(f"Tried {len(api_keys)} different API keys.")
    print("Possible issues:")
    print("  - All keys have reached their daily quota")
    print("  - Network connectivity problems")
    print("  - Invalid API keys")
    print("  - Service temporarily unavailable")
    
    return False

if __name__ == "__main__":
    print("Starting Gemini TTS Voice Test with API Key Rotation...")
    print("This will automatically try different API keys if quota is exhausted.\n")
    
    try:
        success = test_gemini_tts_voice_with_rotation()
        
        if not success:
            print("❌ No audio files were generated successfully.")
            print("Please check your API keys and internet connection.")
            sys.exit(1)
        else:
            print("🎯 Voice test completed successfully with key rotation!")
            
    except Exception as e:
        print(f"❌ Script failed with error: {e}")
        sys.exit(1) 