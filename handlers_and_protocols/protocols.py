from abc import ABC, abstractmethod
from typing import Optional, Any
import io


class EnvironmentHandler(ABC):
    @abstractmethod
    def load_environment(
        self, credentials_env_var: str = "GOOGLE_APPLICATION_CREDENTIALS"
    ) -> None:
        """Load environment variables and credentials"""
        pass


class TTSServiceHandler(ABC):
    @abstractmethod
    def synthesize_text(
        self,
        text: str,
        voice_config: Any = None,
        audio_config: Any = None,
        output_format: str = "mp3",
    ) -> bytes:
        """
        Synthesizes speech from text input

        Args:
            text: Text to convert to speech
            voice_config: Voice configuration object
            audio_config: Audio configuration object
            output_format: Output audio format

        Returns:
            Audio content as bytes
        """
        pass

    @abstractmethod
    def synthesize_markup(
        self,
        markup_text: str,
        voice_config: Any = None,
        audio_config: Any = None,
        output_format: str = "mp3",
    ) -> bytes:
        """
        Synthesizes speech from markup text (SSML/custom markup)

        Args:
            markup_text: Text with markup for pauses, emphasis, etc.
            voice_config: Voice configuration object
            audio_config: Audio configuration object
            output_format: Output audio format

        Returns:
            Audio content as bytes
        """
        pass

    @abstractmethod
    def get_available_voices(self, language_code: str = "en-US") -> list:
        """Get list of available voices for a language"""
        pass


class AudioProcessorHandler(ABC):
    @abstractmethod
    def save_audio(
        self, audio_content: bytes, filename: str, format: str = "wav"
    ) -> str:
        """Save audio content to file"""
        pass

    @abstractmethod
    def create_batch_files(
        self, qa_pairs: list, tts_handler: TTSServiceHandler, **kwargs
    ) -> list:
        """Create separate audio files for each Q&A pair"""
        pass
