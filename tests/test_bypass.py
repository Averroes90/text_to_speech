# test_bypass.py
from google.cloud import texttospeech_v1beta1 as texttospeech
from adapters.google_adapters.google_environment_loader import GoogleEnvironmentHandler

# Initialize once at module level
environment_handler = GoogleEnvironmentHandler()
environment_handler.load_environment()
client = texttospeech.TextToSpeechClient()


def synthesize_bypass(prompt: str) -> bytes:
    """
    Bypass all handlers and call Google TTS directly

    Args:
        prompt: Text to synthesize

    Returns:
        Audio content as bytes
    """
    # Hardcoded settings that match working example
    voice = "Charon"
    language_code = "en-US"
    voice_name = f"{language_code}-Chirp3-HD-{voice}"

    print(f"🔍 Bypass - Testing voice: {voice_name}")
    print(f"🔍 Bypass - Text length: {len(prompt)} chars")

    voice_params = texttospeech.VoiceSelectionParams(
        name=voice_name,
        language_code=language_code,
    )

    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=prompt),
        voice=voice_params,
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
        ),
    )

    return response.audio_content
