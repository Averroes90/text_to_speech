import os
from pathlib import Path
from typing import Optional, List, Any
from handlers_and_protocols.protocols import TTSServiceHandler
from test_bypass import synthesize_bypass


class AudioProcessor:
    """Versatile processor for handling audio file operations and batch processing"""

    def __init__(self, output_dir: str = "output"):
        """
        Initialize audio processor

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_audio(
        self, audio_content: bytes, filename: str, format: str = "mp3"
    ) -> str:
        """
        Save audio content to file

        Args:
            audio_content: Audio bytes from TTS service
            filename: Output filename (without extension)
            format: Audio format (wav, mp3, etc.)

        Returns:
            Full path to saved file
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)
        output_path = self.output_dir / f"{safe_filename}.{format}"

        try:
            with open(output_path, "wb") as audio_file:
                audio_file.write(audio_content)

            return str(output_path)
        except Exception as e:
            raise IOError(f"Error saving audio file {output_path}: {str(e)}")

    def create_batch_files(
        self,
        qa_pairs: List[Any],
        tts_handler: TTSServiceHandler,
        voice_config: Any = None,
        filename_prefix: str = "qa_pair",
    ) -> List[str]:
        """
        Create separate audio files for each Q&A pair

        Args:
            qa_pairs: List of Q&A pair objects
            tts_handler: TTS service handler instance
            voice_config: Voice configuration object
            audio_config: Audio configuration object
            filename_prefix: Prefix for output filenames

        Returns:
            List of paths to created audio files
        """
        file_paths = []

        for i, qa in enumerate(qa_pairs, 1):
            try:
                # Create text for this Q&A
                text = f"Question: {qa.question}. Answer: {qa.answer}."

                # Generate audio using the TTS handler
                audio_content = tts_handler.synthesize_text(text, voice_config)
                # audio_content = synthesize_bypass(text)
                # Create filename
                filename = f"{filename_prefix}_{i:03d}"

                # Save file
                file_path = self.save_audio(audio_content, filename)
                file_paths.append(file_path)

            except Exception as e:
                print(f"Warning: Failed to create audio for Q&A pair {i}: {str(e)}")
                continue

        return file_paths

    def create_batch_files_with_markup(
        self,
        qa_pairs: List[Any],
        tts_handler: TTSServiceHandler,
        voice_config: Any = None,
        audio_config: Any = None,
        filename_prefix: str = "qa_pair",
    ) -> List[str]:
        """
        Create separate audio files for each Q&A pair using markup synthesis

        Args:
            qa_pairs: List of Q&A pair objects
            tts_handler: TTS service handler instance
            voice_config: Voice configuration object
            audio_config: Audio configuration object
            filename_prefix: Prefix for output filenames

        Returns:
            List of paths to created audio files
        """
        file_paths = []

        for i, qa in enumerate(qa_pairs, 1):
            try:
                # Create markup text for this Q&A with pauses
                markup_text = f"Question: [pause short] {qa.question}. [pause medium] Answer: [pause short] {qa.answer}."

                # Generate audio using markup synthesis
                audio_content = tts_handler.synthesize_text(
                    markup_text, voice_config, audio_config
                )

                # Create filename
                filename = f"{filename_prefix}_{i:03d}"

                # Save file
                file_path = self.save_audio(audio_content, filename)
                file_paths.append(file_path)

            except Exception as e:
                print(f"Warning: Failed to create audio for Q&A pair {i}: {str(e)}")
                continue

        return file_paths

    def get_output_info(self) -> dict:
        """
        Get information about the output directory

        Returns:
            Dictionary with output directory info
        """
        if not self.output_dir.exists():
            return {"exists": False, "file_count": 0, "total_size_mb": 0}

        files = list(self.output_dir.glob("*"))
        audio_files = [f for f in files if f.suffix.lower() in [".wav", ".mp3", ".ogg"]]

        total_size = sum(f.stat().st_size for f in files if f.is_file())

        return {
            "exists": True,
            "path": str(self.output_dir),
            "total_files": len(files),
            "audio_files": len(audio_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    def clean_output_directory(self, file_pattern: str = "*") -> int:
        """
        Clean files from output directory

        Args:
            file_pattern: Pattern for files to delete (default: all files)

        Returns:
            Number of files deleted
        """
        deleted_count = 0

        for file_path in self.output_dir.glob(file_pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Warning: Could not delete {file_path}: {str(e)}")

        return deleted_count

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file system usage

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace problematic characters
        import re

        # Replace spaces and special characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = sanitized.strip("._")

        # Ensure it's not too long
        if len(sanitized) > 200:
            sanitized = sanitized[:200]

        # Ensure it's not empty
        if not sanitized:
            sanitized = "audio_file"

        return sanitized

    def create_playlist_file(
        self, audio_files: List[str], playlist_name: str = "playlist"
    ) -> str:
        """
        Create a simple playlist file (.m3u) for the audio files

        Args:
            audio_files: List of audio file paths
            playlist_name: Name for the playlist file

        Returns:
            Path to created playlist file
        """
        playlist_path = self.output_dir / f"{playlist_name}.m3u"

        with open(playlist_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for audio_file in audio_files:
                # Write relative path for portability
                relative_path = Path(audio_file).name
                f.write(f"{relative_path}\n")

        return str(playlist_path)
