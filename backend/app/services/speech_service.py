import logging
import re
import httpx
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text for TTS."""
    # Remove bold/italic markers
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    text = re.sub(r'_+([^_]+)_+', r'\1', text)
    # Remove code blocks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove bullet points
    text = re.sub(r'^[\s]*[-•]\s*', '', text, flags=re.MULTILINE)
    return text.strip()


class SpeechService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.elevenlabs_url = "https://api.elevenlabs.io/v1/text-to-speech"
    
    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.ogg") -> str:
        """Transcribe audio to text using OpenAI Whisper.
        
        Auto-detects language to support both Spanish and English audio inputs.
        """
        try:
            # Create a file-like object - let Whisper auto-detect language
            # This supports both Spanish (student's native language) and English (learning)
            transcript = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, audio_bytes)
            )
            
            logger.info(f"Transcribed audio: {transcript.text[:50]}...")
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using ElevenLabs."""
        # Strip markdown formatting for cleaner TTS
        clean_text = strip_markdown(text)
        
        if not clean_text:
            logger.warning("Empty text after stripping markdown")
            raise ValueError("Empty text for TTS")
        
        # Check if API key is configured
        if not settings.elevenlabs_api_key:
            logger.error("ElevenLabs API key not configured")
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            url = f"{self.elevenlabs_url}/{settings.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.elevenlabs_api_key
            }
            
            data = {
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            logger.info(f"Sending TTS request for: {clean_text[:50]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    raise Exception(f"ElevenLabs API error: {response.status_code}")
                
                logger.info(f"Successfully generated audio ({len(response.content)} bytes)")
                return response.content
                
        except httpx.TimeoutException:
            logger.error("ElevenLabs API timeout")
            raise
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    async def transcribe_from_url(self, file_url: str) -> str:
        """Download audio from URL and transcribe."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url, timeout=30.0)
                response.raise_for_status()
                audio_bytes = response.content
            
            return await self.transcribe_audio(audio_bytes)
            
        except Exception as e:
            logger.error(f"Error downloading/transcribing audio: {e}")
            raise
