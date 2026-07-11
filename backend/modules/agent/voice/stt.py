"""
stt.py — Speech-to-Text (STT) transcription using the Gemini Multimodal API.
"""

import logging
import os
import asyncio
from google import genai
from google.genai import types
from core.config import settings

logger = logging.getLogger(__name__)

def _get_client() -> genai.Client:
    """Instantiate the Gemini client using settings.gemini_api_key."""
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=api_key)

async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    """
    Transcribes raw audio bytes into text using Gemini's native audio understanding.
    """
    if not audio_bytes:
        raise ValueError("Cannot transcribe empty audio.")

    logger.info(f"STT Transcription requested using Gemini (bytes: {len(audio_bytes)}, mime_type: {mime_type})")
    
    def _call_gemini():
        client = _get_client()
        # We use gemini-2.5-flash as the fast multimodal audio understanding model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type,
                ),
                "Please transcribe this audio into plain text. Provide only the spoken words, with clean grammar, and do not append any commentary."
            ]
        )
        return response.text or ""

    try:
        transcription = await asyncio.to_thread(_call_gemini)
        cleaned = transcription.strip()
        logger.info(f"STT Transcription completed: '{cleaned}'")
        return cleaned
    except Exception as e:
        logger.error(f"STT Transcription failed: {e}")
        raise RuntimeError(f"Speech transcription failed: {str(e)}")
