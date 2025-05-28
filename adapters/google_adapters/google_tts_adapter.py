from google.cloud import texttospeech_v1beta1 as texttospeech
from google.api_core.client_options import ClientOptions
from handlers_and_protocols.protocols import TTSServiceHandler, EnvironmentHandler
from .google_environment_loader import GoogleEnvironmentHandler
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import os
from dotenv import load_dotenv
import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    LINEAR16 = texttospeech.AudioEncoding.LINEAR16
    MP3 = texttospeech.AudioEncoding.MP3


@dataclass
class GoogleVoiceConfig:
    language_code: str = "en-US"
    voice_name: str = "en-US-Chirp3-HD-Leda"
    speaking_rate: float = 0.9
    volume_gain_db: float = 0.0


@dataclass
class GoogleAudioConfig:
    format: AudioFormat = AudioFormat.MP3
    sample_rate: int = 24000


class GoogleTTSModelHandler(TTSServiceHandler):
    def __init__(
        self,
        server_region: str = "global",
        environment_handler: EnvironmentHandler = None,
        env_loaded: bool = False,
    ):
        if not env_loaded:
            if environment_handler is None:
                environment_handler = GoogleEnvironmentHandler()
            environment_handler.load_environment()

        self.server_region = server_region

        if self.server_region != "global":
            API_ENDPOINT = f"{server_region}-texttospeech.googleapis.com"
            self.tts_client = texttospeech.TextToSpeechClient(
                client_options=ClientOptions(api_endpoint=API_ENDPOINT)
            )
        else:
            self.tts_client = texttospeech.TextToSpeechClient()

    def synthesize_text(
        self,
        text: str,
        voice_config: Optional[GoogleVoiceConfig] = None,
        audio_config: Optional[GoogleAudioConfig] = None,
        output_format: str = "mp3",
    ) -> bytes:
        if voice_config is None:
            voice_config = GoogleVoiceConfig()
        if audio_config is None:
            audio_config = GoogleAudioConfig()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            name=voice_config.voice_name,
            language_code=voice_config.language_code,
        )

        audio_config_proto = texttospeech.AudioConfig(
            audio_encoding=audio_config.format.value,
            sample_rate_hertz=audio_config.sample_rate,
            speaking_rate=voice_config.speaking_rate,
            volume_gain_db=voice_config.volume_gain_db,
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config_proto
        )

        return response.audio_content

    def synthesize_markup(
        self,
        markup_text: str,
        voice_config: Optional[GoogleVoiceConfig] = None,
        audio_config: Optional[GoogleAudioConfig] = None,
        output_format: str = "mp3",
    ) -> bytes:
        if voice_config is None:
            voice_config = GoogleVoiceConfig()
        if audio_config is None:
            audio_config = GoogleAudioConfig()

        synthesis_input = texttospeech.SynthesisInput(markup=markup_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config.language_code,
            name=voice_config.voice_name,
        )

        audio_config_proto = texttospeech.AudioConfig(
            audio_encoding=audio_config.format.value,
            sample_rate_hertz=audio_config.sample_rate,
            speaking_rate=voice_config.speaking_rate,
            volume_gain_db=voice_config.volume_gain_db,
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config_proto
        )

        return response.audio_content

    def get_available_voices(self, language_code: str = "en-US") -> list:
        """Get list of available voices for a language"""
        voices = self.tts_client.list_voices(language_code=language_code)
        return [
            {
                "name": voice.name,
                "gender": (
                    voice.ssml_gender.name
                    if hasattr(voice, "ssml_gender")
                    else "UNKNOWN"
                ),
                "natural_sample_rate": voice.natural_sample_rate_hertz,
            }
            for voice in voices.voices
        ]


# Voice presets following your configuration pattern
class GoogleVoicePresets:
    """Predefined voice configurations for Google Chirp 3 models"""

    @staticmethod
    def confident_male() -> GoogleVoiceConfig:
        return GoogleVoiceConfig(
            voice_name="en-US-Chirp3-HD-Charon", speaking_rate=0.9, volume_gain_db=2.0
        )

    @staticmethod
    def professional_female() -> GoogleVoiceConfig:
        return GoogleVoiceConfig(
            voice_name="en-US-Chirp3-HD-Leda", speaking_rate=0.9, volume_gain_db=1.0
        )

    @staticmethod
    def authoritative_neutral() -> GoogleVoiceConfig:
        return GoogleVoiceConfig(
            voice_name="en-US-Chirp3-HD-Charon", speaking_rate=0.85, volume_gain_db=3.0
        )

    @staticmethod
    def fast_review() -> GoogleVoiceConfig:
        return GoogleVoiceConfig(
            voice_name="en-US-Chirp3-HD-Leda", speaking_rate=2.0, volume_gain_db=1.0
        )
