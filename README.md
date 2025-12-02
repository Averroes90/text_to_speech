# text_to_speech
# Interview Q&A Text-to-Speech Pipeline

Convert interview Q&A documents into high-quality speech audio using Google Cloud TTS with Chirp 3 voices.

## Quick Start

### Prerequisites
- Python 3.12+
- Poetry installed
- Google Cloud account with Text-to-Speech API enabled

### Installation

1. **Clone and navigate to project:**
```bash
cd text_to_speech
```

2. **Install dependencies:**
```bash
poetry install
```

3. **Set up Google Cloud credentials:**
   - Download your service account JSON key from Google Cloud Console
   - Place it in `config/credentials.json`
   - Create `.env` file in project root:
```
   GOOGLE_APPLICATION_CREDENTIALS=config/credentials.json
```

### Usage

**Basic command:**
```bash
poetry run python main.py input/YOUR_FILE.docx
```

**With options:**
```bash
# Custom voice and output name
poetry run python main.py input/YOUR_FILE.docx --voice confident_male --output-name my_prep

# Batch mode (separate files for each Q&A)
poetry run python main.py input/YOUR_FILE.docx --batch

# All options
poetry run python main.py input/YOUR_FILE.docx \
  --voice confident_male \
  --output-name leadership_prep \
  --batch \
  --region global
```

### Command Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--voice` | `-v` | `professional_female` | Voice preset (`professional_female` or `confident_male`) |
| `--output-name` | `-o` | `interview_dialogue` | Output filename (without extension) |
| `--batch` | `-b` | Off | Create separate files for each Q&A pair |
| `--region` | `-r` | `global` | Google Cloud region (`global` recommended) |
| `--service` | `-s` | `google` | TTS service provider |

### Document Format

Your DOCX file should contain Q&A pairs in one of these formats:

**Format 1: Q: / A:**
```
Q: What's your biggest strength?
A: My biggest strength is problem-solving...

Q: Tell me about a challenge.
A: Once I faced a situation where...
```

**Format 2: Numbered Q / A:**
```
Q1 What's your biggest strength?
A: My biggest strength is problem-solving...

Q2 Tell me about a challenge.
A: Once I faced a situation where...
```

**Format 3: Question: / Answer:**
```
Question: What's your biggest strength?
Answer: My biggest strength is problem-solving...
```

**Format 4: Numbered with Answer:**
```
1. What's your biggest strength?
Answer: My biggest strength is problem-solving...
```

**Format 5: Natural question marks:**
```
What's your biggest strength?
My biggest strength is problem-solving...
```

**Note:** You can mix formats in the same document - the parser will detect all patterns.
That's it! The new format will now be recognized automatically.

### Output

**Single mode (default):**
- Creates one MP3 file with all Q&A pairs
- Includes strategic pauses between questions
- Located in `output/` directory

**Batch mode:**
- Creates separate MP3 files for each Q&A pair
- Files named: `qa_pair_001.mp3`, `qa_pair_002.mp3`, etc.
- Useful for random practice or playlist creation

## Common Issues

### "Command not found: python"
Use Poetry to run commands:
```bash
poetry run python main.py ...
```

### "Voice not found" error
Make sure `--region global` is set (default):
```bash
poetry run python main.py input/file.docx --region global
```

### "5000 byte limit" error
Your document is too long. Use batch mode:
```bash
poetry run python main.py input/file.docx --batch
```

### No audio in output file
Check that:
1. Google Cloud credentials are properly set up
2. Text-to-Speech API is enabled in Google Cloud Console
3. Using `--region global` (Chirp 3 voices require global endpoint)

### Import/cache issues
Clear Python cache:
```bash
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Project Structure
```
text_to_speech/
├── adapters/
│   └── google_adapters/
│       ├── google_environment_loader.py    # Credentials handling
│       └── google_tts_adapter.py           # Google TTS implementation
├── handlers_and_protocols/
│   ├── protocols.py                        # Interface definitions
│   └── handlers.py                         # Factory methods
├── src/
│   ├── document_processor.py               # DOCX parsing & formatting
│   ├── audio_processor.py                  # Audio file handling
│   └── pipeline.py                         # Main orchestration
├── config/
│   ├── settings.py                         # Configuration
│   └── credentials.json                    # Google Cloud credentials (not in git)
├── input/                                  # Place DOCX files here
├── output/                                 # Generated audio files
├── main.py                                 # CLI entry point
├── .env                                    # Environment variables (not in git)
└── pyproject.toml                          # Poetry dependencies
```

## Voice Presets

### `professional_female`
- Voice: en-US-Chirp3-HD-Leda
- Speaking rate: 0.9x (slightly slower for clarity)
- Volume: +1.0 dB

### `confident_male`
- Voice: en-US-Chirp3-HD-Charon
- Speaking rate: 0.9x (slightly slower for clarity)
- Volume: +2.0 dB

## Advanced Usage

### List available voices:
```bash
poetry run python main.py voices
```

### Update dependencies:
```bash
poetry update
poetry add package-name@latest  # Update specific package
```

### Add new dependencies:
```bash
poetry add package-name
```

### Debugging:
Enable debug logging by editing `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Memory Optimization Tips

For interview preparation, the audio files work best when:
1. **Listen during light activity** (walking, commuting)
2. **Use spaced repetition** (Day 1, 3, 7, 14)
3. **Vary playback speed** (0.8x for learning, 1.2x for review)
4. **Play during first 3 hours of sleep** for memory consolidation
5. **Create multiple versions** with different background music

## Dependencies

- `google-cloud-texttospeech` - Google TTS API client
- `python-docx` - DOCX file processing
- `pydub` - Audio file manipulation
- `click` - CLI framework
- `python-dotenv` - Environment variable management

## Google Cloud Setup

1. **Create project:** https://console.cloud.google.com
2. **Enable API:** Cloud Text-to-Speech API
3. **Create service account:**
   - IAM & Admin → Service Accounts → Create Service Account
   - Grant role: "Cloud Text-to-Speech API User"
4. **Download key:**
   - Actions → Manage Keys → Add Key → Create New Key → JSON
   - Save as `config/credentials.json`

## License

For personal use only. Ensure compliance with Google Cloud TTS terms of service.

## Support

For issues with:
- **Google Cloud:** Check credentials and API enablement
- **Document parsing:** Verify Q&A format in DOCX
- **Audio quality:** Adjust voice preset or speaking rate
- **File size:** Use batch mode for large documents

## Quick Reference
```bash
# Standard workflow
poetry run python main.py input/interview.docx

# High-quality male voice
poetry run python main.py input/interview.docx --voice confident_male

# Separate files for each Q&A
poetry run python main.py input/interview.docx --batch

# Custom output location
poetry run python main.py input/interview.docx -o my_custom_name

# Combine multiple options
poetry run python main.py input/interview.docx \
  --voice confident_male \
  --output-name tech_interview \
  --batch
```

## Notes

- **Region:** Always use `global` region for Chirp 3 voices
- **File size:** Google TTS has 5000-byte limit per request; batch mode automatically handles this
- **Audio format:** Outputs MP3 format by default
- **Pauses:** Automatic strategic pauses added between Q&A pairs using markup
- **Cache:** If imports seem broken, clear `__pycache__` directories

---

Last updated: December 2024
