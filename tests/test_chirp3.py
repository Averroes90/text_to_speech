# test_chirp3.py
from google.cloud import texttospeech_v1beta1 as texttospeech
from handlers_and_protocols.handlers import GoogleEnvironmentHandler
import utils

environment_handler = GoogleEnvironmentHandler()
environment_handler.load_environment()
client = texttospeech.TextToSpeechClient()

# Exact copy from Google's example
# prompt = "Hello world! I am Chirp 3"
prompt = utils.load_object_from_pickle("QApair1.pkl")
print(f"aaaaaaaaaaaaaaaa prompt: {prompt}")
voice = "Charon"
language_code = "en-US"
voice_name = f"{language_code}-Chirp3-HD-{voice}"

print(f"Testing voice: {voice_name}")

voice = texttospeech.VoiceSelectionParams(
    name=voice_name,
    language_code=language_code,
)

response = client.synthesize_speech(
    input=texttospeech.SynthesisInput(text=prompt),
    voice=voice,
    audio_config=texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        sample_rate_hertz=24000,
        speaking_rate=0.9,
        volume_gain_db=2.0,
    ),
)

with open("test_output.mp3", "wb") as out:
    out.write(response.audio_content)
    print("✅ Success! Audio saved to test_output.mp3")
