from .protocols import EnvironmentHandler, TTSServiceHandler, AudioProcessorHandler
from adapters.google_adapters.google_environment_loader import GoogleEnvironmentHandler
from adapters.google_adapters.google_tts_adapter import GoogleTTSModelHandler
from src.audio_processor import AudioProcessor


def get_environment_handler(service: str) -> EnvironmentHandler:
    """Factory method for environment handlers"""
    if service.lower() == "google":
        return GoogleEnvironmentHandler()
    # Add other services as needed
    # elif service.lower() == "azure":
    #     return AzureEnvironmentHandler()
    else:
        raise ValueError(f"Unsupported service: {service}")


def get_tts_handler(service: str, **kwargs) -> TTSServiceHandler:
    """Factory method for TTS service handlers"""
    if service.lower() == "google":
        return GoogleTTSModelHandler(**kwargs)
    # elif service.lower() == "azure":
    #     return AzureTTSModelHandler(**kwargs)
    # elif service.lower() == "openai":
    #     return OpenAITTSModelHandler(**kwargs)
    else:
        raise ValueError(f"Unsupported TTS service: {service}")


def get_audio_processor(
    processor_type: str = "default", **kwargs
) -> AudioProcessorHandler:
    """Factory method for audio processors"""
    if processor_type.lower() == "default":
        return AudioProcessor(**kwargs)
    else:
        raise ValueError(f"Unsupported audio processor: {processor_type}")
