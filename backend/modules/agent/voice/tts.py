"""
tts.py — Text-to-Speech (TTS) synthesis using the Google Gemini Multimodal API (gemini-3.1-flash-tts-preview), falling back to gTTS if the key is invalid or not set.
"""

import logging
import io
import asyncio
import wave
from google import genai
from google.genai import types as genai_types
from gtts import gTTS
from core.config import settings

logger = logging.getLogger(__name__)

def _get_client() -> genai.Client:
    """Instantiate the Gemini client using settings.gemini_api_key."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)

def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, num_channels: int = 1, sampwidth: int = 2) -> bytes:
    """Wraps raw 16-bit PCM audio bytes in a standard RIFF/WAV container."""
    wav_buf = io.BytesIO()
    with wave.open(wav_buf, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sampwidth)  # 2 bytes = 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return wav_buf.getvalue()

async def synthesize_speech(text: str) -> bytes:
    """
    Converts a text string into spoken audio bytes (WAV/MP3 format).
    Uses Gemini's native audio model (gemini-3.1-flash-tts-preview) for natural spoken audio.
    Falls back to gTTS if settings.gemini_api_key is missing or calls fail.
    """
    if not text:
        return b""

    # Clean markdown formatting marks from text before reading
    clean_text = text.replace("**", "").replace("*", "").replace("`", "").replace("#", "").strip()
    if not clean_text:
        return b""

    # 1. Try Gemini Audio Modality first (Requires GEMINI_API_KEY)
    if settings.gemini_api_key and settings.gemini_api_key != "test_gemini_key":
        logger.info(f"Gemini TTS Speech Synthesis requested using gemini-3.1-flash-tts-preview (text length: {len(clean_text)})")
        
        def _call_gemini_audio():
            client = _get_client()
            # Request audio output using the specialized TTS model
            response = client.models.generate_content(
                model="gemini-3.1-flash-tts-preview",
                contents=clean_text,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=genai_types.SpeechConfig(
                        voice_config=genai_types.VoiceConfig(
                            prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                                voice_name="Kore"  # Voices available: Kore, Puck, Charon, Fenrir, Aoede
                            )
                        )
                    )
                )
            )
            
            raw_pcm = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        raw_pcm = part.inline_data.data
                        break
            
            if raw_pcm:
                # Wrap the raw 24kHz 16-bit PCM bytes inside a standard playable WAV file
                return pcm_to_wav(raw_pcm, sample_rate=24000, num_channels=1, sampwidth=2)
            return None

        try:
            audio_data = await asyncio.to_thread(_call_gemini_audio)
            if audio_data:
                logger.info(f"Gemini TTS Speech Synthesis completed successfully (WAV bytes: {len(audio_data)})")
                return audio_data
            else:
                logger.warning("Gemini API succeeded but returned no audio inline data. Falling back to gTTS.")
        except Exception as e:
            logger.error(f"Gemini TTS failed, falling back to gTTS: {e}")

    # 2. Fallback to gTTS (Google Translate free offline engine)
    logger.info(f"gTTS Speech Synthesis requested (text length: {len(clean_text)})")
    def _run_gtts():
        tts = gTTS(text=clean_text, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()

    try:
        audio_bytes = await asyncio.to_thread(_run_gtts)
        logger.info(f"gTTS Speech Synthesis completed successfully (bytes length: {len(audio_bytes)})")
        return audio_bytes
    except Exception as e:
        logger.error(f"gTTS Speech Synthesis failed: {e}")
        raise RuntimeError(f"Speech synthesis failed: {str(e)}")
