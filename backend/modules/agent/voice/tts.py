"""
tts.py — Text-to-Speech (TTS) synthesis using the gTTS (Google Text-to-Speech) library.
"""

import logging
import io
import asyncio
from gtts import gTTS

logger = logging.getLogger(__name__)

async def synthesize_speech(text: str) -> bytes:
    """
    Converts a text string into spoken audio bytes (MP3 format) using gTTS.
    """
    if not text:
        return b""

    # Clean markdown formatting marks from text before reading
    clean_text = text.replace("**", "").replace("*", "").replace("`", "").replace("#", "").strip()
    if not clean_text:
        return b""

    logger.info(f"TTS Speech Synthesis requested (text length: {len(clean_text)})")
    
    def _run_gtts():
        tts = gTTS(text=clean_text, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()

    try:
        audio_bytes = await asyncio.to_thread(_run_gtts)
        logger.info(f"TTS Speech Synthesis completed successfully (bytes length: {len(audio_bytes)})")
        return audio_bytes
    except Exception as e:
        logger.error(f"TTS Speech Synthesis failed: {e}")
        raise RuntimeError(f"Speech synthesis failed: {str(e)}")
