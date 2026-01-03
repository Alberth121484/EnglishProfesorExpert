import logging
import httpx
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.elevenlabs_url = "https://api.elevenlabs.io/v1/text-to-speech"
    
    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.ogg") -> str:
        """Transcribe audio to text using OpenAI Whisper."""
        try:
            # Create a file-like object
            transcript = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, audio_bytes),
                language="es"  # Hint that input might be Spanish
            )
            
            logger.info(f"Transcribed audio: {transcript.text[:50]}...")
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using ElevenLabs."""
        try:
            url = f"{self.elevenlabs_url}/{settings.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                
                logger.info(f"Generated audio for text: {text[:50]}...")
                return response.content
                
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
