from handlers_and_protocols.handlers import get_tts_handler
from adapters.google_adapters.google_tts_adapter import GoogleVoicePresets
from .document_processor import DocumentProcessor
from .audio_processor import AudioProcessor
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSPipeline:
    def __init__(self, service: str = "google", server_region: str = "us-central1"):
        self.service = service
        self.doc_processor = DocumentProcessor()
        self.tts_handler = get_tts_handler(service=service, server_region=server_region)
        self.audio_processor = AudioProcessor()

    def process_document(
        self,
        docx_path: str,
        output_name: str = "interview_dialogue",
        voice_preset: str = "professional_female",
        batch_mode: bool = False,
    ) -> str:
        logger.info(f"Processing document: {docx_path}")

        # Step 1: Extract text and Q&A pairs
        text = self.doc_processor.read_docx(docx_path)
        qa_pairs = self.doc_processor.extract_qa_pairs(text)

        if not qa_pairs:
            raise ValueError("No Q&A pairs found in document.")

        logger.info(f"Found {len(qa_pairs)} Q&A pairs")

        # Step 2: Get voice configuration
        voice_config = getattr(GoogleVoicePresets, voice_preset)()

        # Step 3: Generate audio
        if batch_mode:
            return self._process_batch_mode(qa_pairs, output_name, voice_config)
        else:
            return self._process_single_mode(qa_pairs, output_name, voice_config)

    def _process_single_mode(self, qa_pairs, output_name, voice_config):
        """Create single audio file, with automatic batching for long content"""

        # Create speech text with pauses
        speech_text = self.doc_processor.create_speech_text_with_pauses(
            qa_pairs, "interview"
        )

        # Check size before attempting synthesis
        text_bytes = len(speech_text.encode("utf-8"))
        logger.info(f"Generating audio for {len(qa_pairs)} Q&A pairs...")
        logger.info(f"Speech text: {len(speech_text)} characters, {text_bytes} bytes")

        # If too long, automatically use batch-and-combine approach
        if text_bytes > 4500:  # Leave buffer under 5000-byte limit
            logger.warning(f"Text exceeds Google TTS limit ({text_bytes} > 4500 bytes)")
            logger.info("Automatically switching to batch-and-combine mode...")
            return self._process_single_mode_with_batching(
                qa_pairs, output_name, voice_config
            )

        # If under limit, proceed normally
        logger.info("Text under limit, using single synthesis...")
        audio_content = self.tts_handler.synthesize_text(speech_text, voice_config)

        output_path = self.audio_processor.save_audio(
            audio_content, output_name, format="mp3"
        )
        logger.info(f"Audio saved to: {output_path}")

        return output_path

    def _process_single_mode_with_batching(self, qa_pairs, output_name, voice_config):
        """Create single file by generating and combining individual Q&A audio files"""

        logger.info("Creating individual audio files for each Q&A...")

        # Generate individual files
        temp_files = self.audio_processor.create_batch_files(
            qa_pairs=qa_pairs,
            tts_handler=self.tts_handler,
            voice_config=voice_config,
            filename_prefix="temp_qa",
        )

        logger.info(f"Combining {len(temp_files)} audio files...")

        # Combine all files into one
        try:
            from pydub import AudioSegment

            combined = AudioSegment.empty()

            for i, file_path in enumerate(temp_files):
                logger.debug(f"Adding file {i+1}/{len(temp_files)}: {file_path}")
                audio_segment = AudioSegment.from_mp3(file_path)
                combined += audio_segment

                # Add pause between Q&As (except after last one)
                if i < len(temp_files) - 1:
                    combined += AudioSegment.silent(duration=1500)  # 1.5 second pause

            # Export combined audio
            output_path = self.audio_processor.save_audio(
                combined.export(format="mp3").read(), output_name, format="mp3"
            )

            # Clean up temporary files
            logger.info("Cleaning up temporary files...")
            for file_path in temp_files:
                try:
                    os.remove(file_path)
                except:
                    pass  # Ignore cleanup errors

            logger.info(f"Combined audio saved to: {output_path}")
            return output_path

        except ImportError:
            logger.error("pydub is required for combining audio files")
            logger.info("Install with: pip install pydub")
            logger.info(f"Individual files saved as: {temp_files}")
            return temp_files
        except Exception as e:
            logger.error(f"Error combining files: {e}")
            logger.info(f"Individual files saved as: {temp_files}")
            return temp_files

    def _process_batch_mode(self, qa_pairs, output_name, voice_config):
        logger.info("Generating batch audio files...")

        file_paths = self.audio_processor.create_batch_files(
            qa_pairs, self.tts_handler, voice_config=voice_config
        )

        logger.info(f"Created {len(file_paths)} audio files")
        return file_paths
