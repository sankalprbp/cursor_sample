"""
Audio Processing Service
Handles audio format conversion and optimization for voice conversations
"""

import asyncio
import logging
import io
import hashlib
import time
from typing import Optional, Dict, Tuple
from pydub import AudioSegment
from pydub.utils import make_chunks
import base64
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for processing audio data for voice conversations with caching"""
    
    def __init__(self):
        # Twilio Media Streams audio format settings
        self.twilio_sample_rate = 8000
        self.twilio_channels = 1
        self.twilio_format = "mulaw"
        
        # OpenAI Whisper preferred format
        self.whisper_sample_rate = 16000
        self.whisper_channels = 1
        self.whisper_format = "wav"
        
        # ElevenLabs output format
        self.elevenlabs_sample_rate = 22050
        self.elevenlabs_channels = 1
        self.elevenlabs_format = "mp3"
        
        # Audio caching
        self.audio_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self.cache_max_size = 100  # Maximum number of cached audio files
        self.cache_ttl_hours = 24  # Time to live for cached audio
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Frequently used responses cache
        self.common_responses = {
            "greeting": "Hello! How can I help you today?",
            "goodbye": "Thank you for calling. Have a great day!",
            "hold": "Please hold on for just a moment.",
            "sorry": "I'm sorry, I didn't quite catch that. Could you please repeat?",
            "thinking": "Let me think about that for a moment.",
            "transfer": "I'll transfer you to someone who can better assist you."
        }
    
    async def convert_for_whisper(self, audio_data: bytes) -> bytes:
        """Convert Twilio audio to format suitable for OpenAI Whisper"""
        
        try:
            # Twilio sends mulaw encoded audio at 8kHz
            # Convert to WAV format for Whisper
            
            # Create AudioSegment from mulaw data
            audio = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=1,  # mulaw is 8-bit
                frame_rate=self.twilio_sample_rate,
                channels=self.twilio_channels
            )
            
            # Convert to 16kHz WAV for better Whisper performance
            audio = audio.set_frame_rate(self.whisper_sample_rate)
            audio = audio.set_channels(self.whisper_channels)
            
            # Export as WAV
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            return wav_buffer.read()
        
        except Exception as e:
            logger.error(f"Error converting audio for Whisper: {e}")
            return audio_data  # Return original if conversion fails
    
    async def convert_for_twilio(self, audio_data: bytes) -> bytes:
        """Convert ElevenLabs audio to format suitable for Twilio ConversationRelay"""
        
        try:
            # ElevenLabs typically returns MP3 at 22kHz
            # Convert to mulaw at 8kHz for Twilio
            
            # Load audio data
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Convert to Twilio's expected format
            audio = audio.set_frame_rate(self.twilio_sample_rate)
            audio = audio.set_channels(self.twilio_channels)
            
            # Convert to mulaw encoding
            mulaw_buffer = io.BytesIO()
            audio.export(mulaw_buffer, format="raw", codec="pcm_mulaw")
            mulaw_buffer.seek(0)
            
            return mulaw_buffer.read()
        
        except Exception as e:
            logger.error(f"Error converting audio for Twilio: {e}")
            
            # Fallback: try to convert as WAV
            try:
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
                audio = audio.set_frame_rate(self.twilio_sample_rate)
                audio = audio.set_channels(self.twilio_channels)
                
                mulaw_buffer = io.BytesIO()
                audio.export(mulaw_buffer, format="raw", codec="pcm_mulaw")
                mulaw_buffer.seek(0)
                
                return mulaw_buffer.read()
            
            except Exception as e2:
                logger.error(f"Fallback audio conversion failed: {e2}")
                return audio_data  # Return original if all conversions fail
    
    async def get_cached_audio(self, text: str, voice_settings: Optional[Dict] = None) -> Optional[bytes]:
        """Get cached audio for text if available"""
        
        try:
            # Create cache key from text and voice settings
            cache_key = self._generate_cache_key(text, voice_settings)
            
            # Check if audio is in cache
            if cache_key in self.audio_cache:
                audio_data, cached_time = self.audio_cache[cache_key]
                
                # Check if cache entry is still valid
                if datetime.utcnow() - cached_time < timedelta(hours=self.cache_ttl_hours):
                    self.cache_hits += 1
                    logger.debug(f"Audio cache hit for: {text[:50]}...")
                    return audio_data
                else:
                    # Remove expired entry
                    del self.audio_cache[cache_key]
            
            self.cache_misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached audio: {e}")
            return None
    
    async def cache_audio(self, text: str, audio_data: bytes, voice_settings: Optional[Dict] = None):
        """Cache audio data for future use"""
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(text, voice_settings)
            
            # Clean up cache if it's getting too large
            if len(self.audio_cache) >= self.cache_max_size:
                await self._cleanup_cache()
            
            # Store in cache
            self.audio_cache[cache_key] = (audio_data, datetime.utcnow())
            logger.debug(f"Cached audio for: {text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error caching audio: {e}")
    
    def _generate_cache_key(self, text: str, voice_settings: Optional[Dict] = None) -> str:
        """Generate a unique cache key for text and voice settings"""
        
        # Normalize text
        normalized_text = text.lower().strip()
        
        # Include voice settings in key
        settings_str = ""
        if voice_settings:
            settings_str = str(sorted(voice_settings.items()))
        
        # Create hash
        key_string = f"{normalized_text}|{settings_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _cleanup_cache(self):
        """Clean up old cache entries"""
        
        try:
            current_time = datetime.utcnow()
            expired_keys = []
            
            # Find expired entries
            for key, (audio_data, cached_time) in self.audio_cache.items():
                if current_time - cached_time > timedelta(hours=self.cache_ttl_hours):
                    expired_keys.append(key)
            
            # Remove expired entries
            for key in expired_keys:
                del self.audio_cache[key]
            
            # If still too large, remove oldest entries
            if len(self.audio_cache) >= self.cache_max_size:
                # Sort by timestamp and remove oldest
                sorted_items = sorted(
                    self.audio_cache.items(),
                    key=lambda x: x[1][1]  # Sort by timestamp
                )
                
                # Remove oldest 20% of entries
                remove_count = max(1, len(sorted_items) // 5)
                for i in range(remove_count):
                    key = sorted_items[i][0]
                    del self.audio_cache[key]
            
            logger.info(f"Cache cleanup completed. Size: {len(self.audio_cache)}")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    async def preload_common_responses(self, voice_settings: Optional[Dict] = None):
        """Preload common responses into cache"""
        
        try:
            from app.services.voice_agent import voice_agent_service
            
            logger.info("Preloading common responses into audio cache...")
            
            for response_type, text in self.common_responses.items():
                # Check if already cached
                if not await self.get_cached_audio(text, voice_settings):
                    try:
                        # Generate audio (this would normally call ElevenLabs)
                        # For now, we'll just create a placeholder
                        audio_data = await voice_agent_service._text_to_speech(text, None)
                        
                        if audio_data:
                            await self.cache_audio(text, audio_data, voice_settings)
                            logger.debug(f"Preloaded: {response_type}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to preload {response_type}: {e}")
            
            logger.info("Common responses preloading completed")
            
        except Exception as e:
            logger.error(f"Error preloading common responses: {e}")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache performance statistics"""
        
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self.audio_cache),
            "max_size": self.cache_max_size,
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_hours": self.cache_ttl_hours
        }
    
    async def clear_cache(self):
        """Clear all cached audio"""
        
        self.audio_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Audio cache cleared")
    
    async def optimize_for_streaming(self, audio_data: bytes, chunk_size: int = 1024) -> list:
        """Split audio into chunks for streaming"""
        
        try:
            # Load audio
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Create chunks for streaming
            chunk_length_ms = chunk_size  # milliseconds
            chunks = make_chunks(audio, chunk_length_ms)
            
            # Convert each chunk to bytes
            chunk_data = []
            for chunk in chunks:
                chunk_buffer = io.BytesIO()
                chunk.export(chunk_buffer, format="raw", codec="pcm_mulaw")
                chunk_buffer.seek(0)
                chunk_data.append(chunk_buffer.read())
            
            return chunk_data
        
        except Exception as e:
            logger.error(f"Error optimizing audio for streaming: {e}")
            return [audio_data]  # Return as single chunk if optimization fails
    
    async def validate_audio_format(self, audio_data: bytes) -> bool:
        """Validate that audio data is in a supported format"""
        
        try:
            # Try to load as different formats
            formats_to_try = ["mp3", "wav", "raw"]
            
            for fmt in formats_to_try:
                try:
                    if fmt == "raw":
                        # Try as mulaw raw data
                        AudioSegment.from_raw(
                            io.BytesIO(audio_data),
                            sample_width=1,
                            frame_rate=8000,
                            channels=1
                        )
                    else:
                        AudioSegment.from_file(io.BytesIO(audio_data), format=fmt)
                    
                    return True
                except:
                    continue
            
            return False
        
        except Exception as e:
            logger.error(f"Error validating audio format: {e}")
            return False
    
    async def get_audio_info(self, audio_data: bytes) -> Optional[dict]:
        """Get information about audio data"""
        
        try:
            # Try to load as MP3 first (ElevenLabs default)
            try:
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            except:
                # Try as WAV
                try:
                    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
                except:
                    # Try as raw mulaw
                    audio = AudioSegment.from_raw(
                        io.BytesIO(audio_data),
                        sample_width=1,
                        frame_rate=8000,
                        channels=1
                    )
            
            return {
                "duration_ms": len(audio),
                "frame_rate": audio.frame_rate,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "max_possible_amplitude": audio.max_possible_amplitude
            }
        
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return None
    
    async def normalize_audio_level(self, audio_data: bytes, target_dBFS: float = -20.0) -> bytes:
        """Normalize audio level to target dBFS"""
        
        try:
            # Load audio
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Normalize to target level
            change_in_dBFS = target_dBFS - audio.dBFS
            normalized_audio = audio.apply_gain(change_in_dBFS)
            
            # Export back to bytes
            output_buffer = io.BytesIO()
            normalized_audio.export(output_buffer, format="mp3")
            output_buffer.seek(0)
            
            return output_buffer.read()
        
        except Exception as e:
            logger.error(f"Error normalizing audio level: {e}")
            return audio_data  # Return original if normalization fails
    
    async def add_silence_padding(self, audio_data: bytes, padding_ms: int = 100) -> bytes:
        """Add silence padding to beginning and end of audio"""
        
        try:
            # Load audio
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Create silence
            silence = AudioSegment.silent(duration=padding_ms)
            
            # Add padding
            padded_audio = silence + audio + silence
            
            # Export back to bytes
            output_buffer = io.BytesIO()
            padded_audio.export(output_buffer, format="mp3")
            output_buffer.seek(0)
            
            return output_buffer.read()
        
        except Exception as e:
            logger.error(f"Error adding silence padding: {e}")
            return audio_data  # Return original if padding fails


# Global instance
audio_processor = AudioProcessor()