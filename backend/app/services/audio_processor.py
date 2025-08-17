"""
Audio Processing Service
Handles audio format conversion and optimization for voice conversations
"""

import asyncio
import logging
import io
from typing import Optional
from pydub import AudioSegment
from pydub.utils import make_chunks
import base64

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for processing audio data for voice conversations"""
    
    def __init__(self):
        # Twilio ConversationRelay audio format settings
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