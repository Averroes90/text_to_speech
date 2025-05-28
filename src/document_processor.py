from docx import Document
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class QAPair:
    """Represents a question-answer pair"""

    question: str
    answer: str
    category: str = "general"


class DocumentProcessor:
    """Versatile processor for extracting and formatting Q&A content from DOCX documents"""

    def __init__(self):
        # Multiple patterns to handle different Q&A formats
        self.qa_patterns = [
            r"Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)",  # Q: ... A: ... format
            r"Question:\s*(.*?)\s*Answer:\s*(.*?)(?=Question:|$)",  # Question: ... Answer: ...
            r"(\d+\.\s*.*?)\s*Answer:\s*(.*?)(?=\d+\.|$)",  # 1. Question Answer: ...
            r"(\d+\)\s*.*?)\s*Answer:\s*(.*?)(?=\d+\)|$)",  # 1) Question Answer: ...
            r"([^\n]+\?)\s*([^Q\n]+?)(?=\n.*\?|$)",  # Question? Answer (natural format)
        ]

    def read_docx(self, file_path: str) -> str:
        """
        Extract all text from DOCX file

        Args:
            file_path: Path to DOCX file

        Returns:
            Full text content as string
        """
        try:
            doc = Document(file_path)
            full_text = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Skip empty paragraphs
                    full_text.append(paragraph.text)

            return "\n".join(full_text)
        except Exception as e:
            raise ValueError(f"Error reading DOCX file {file_path}: {str(e)}")

    def extract_qa_pairs(self, text: str) -> List[QAPair]:
        """
        Extract Q&A pairs from text using multiple patterns

        Args:
            text: Raw text content

        Returns:
            List of QAPair objects
        """
        qa_pairs = []

        for pattern in self.qa_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                question = self._clean_text(match[0])
                answer = self._clean_text(match[1])

                if question and answer and len(question) > 5 and len(answer) > 5:
                    # Avoid duplicates
                    if not any(
                        qa.question.lower() == question.lower() for qa in qa_pairs
                    ):
                        qa_pairs.append(QAPair(question=question, answer=answer))

        return qa_pairs

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for speech synthesis

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize
        text = re.sub(r"\s+", " ", text.strip())

        # Remove common document artifacts
        text = re.sub(r"[\r\n]+", " ", text)
        text = re.sub(r'\s*[""' "]\s*", '"', text)  # Normalize quotes
        text = re.sub(r"\s*[–—]\s*", " - ", text)  # Normalize dashes

        # Remove bullet points and numbering artifacts
        text = re.sub(r"^\s*[\•·▪▫]\s*", "", text)
        text = re.sub(r"^\s*\d+[\.\)]\s*", "", text)

        return text.strip()

    def create_speech_text(
        self, qa_pairs: List[QAPair], format_style: str = "simple"
    ) -> str:
        """
        Convert Q&A pairs to speech-optimized text (basic version without markup)

        Args:
            qa_pairs: List of Q&A pairs
            format_style: Format style ('simple', 'interview', 'dialogue')

        Returns:
            Speech-ready text
        """
        if format_style == "interview":
            return self._format_interview_style(qa_pairs)
        elif format_style == "dialogue":
            return self._format_dialogue_style(qa_pairs)
        else:
            return self._format_simple_style(qa_pairs)

    def create_speech_text_with_pauses(
        self, qa_pairs: List[QAPair], format_style: str = "interview"
    ) -> str:
        """
        Convert Q&A pairs to speech-optimized text with markup pauses for Google TTS

        Args:
            qa_pairs: List of Q&A pairs
            format_style: Format style ('interview', 'dialogue', 'simple')

        Returns:
            Speech-ready text with pause markup
        """
        if format_style == "interview":
            return self._format_interview_with_pauses(qa_pairs)
        elif format_style == "dialogue":
            return self._format_dialogue_with_pauses(qa_pairs)
        else:
            return self._format_simple_with_pauses(qa_pairs)

    # Basic formatting methods (no markup)
    def _format_interview_style(self, qa_pairs: List[QAPair]) -> str:
        """Format as realistic interview dialogue"""
        speech_parts = []

        for i, qa in enumerate(qa_pairs, 1):
            speech_parts.append(f"Interview question {i}.")
            speech_parts.append(qa.question)
            speech_parts.append("Your response:")
            speech_parts.append(qa.answer)
            speech_parts.append("... ... ...")  # Spoken pause

        return " ".join(speech_parts)

    def _format_dialogue_style(self, qa_pairs: List[QAPair]) -> str:
        """Format as conversational dialogue"""
        speech_parts = []

        for qa in qa_pairs:
            speech_parts.append(f"Question: {qa.question}")
            speech_parts.append(f"Answer: {qa.answer}")
            speech_parts.append("... ... ...")  # Spoken pause

        return " ".join(speech_parts)

    def _format_simple_style(self, qa_pairs: List[QAPair]) -> str:
        """Simple concatenation with pauses"""
        speech_parts = []

        for qa in qa_pairs:
            speech_parts.append(qa.question)
            speech_parts.append(qa.answer)
            speech_parts.append("... ... ...")  # Spoken pause

        return " ".join(speech_parts)

    # Markup formatting methods (with Google TTS pause markup)
    def _format_interview_with_pauses(self, qa_pairs: List[QAPair]) -> str:
        """Format as realistic interview dialogue with strategic pauses"""
        speech_parts = []

        for i, qa in enumerate(qa_pairs, 1):
            speech_parts.append(f"Interview question {i}. [pause short]")
            speech_parts.append(qa.question)
            speech_parts.append("[pause long] Your response: [pause short]")
            speech_parts.append(qa.answer)
            speech_parts.append("[pause long]")  # Long pause between questions

        return " ".join(speech_parts)

    def _format_dialogue_with_pauses(self, qa_pairs: List[QAPair]) -> str:
        """Format as conversational dialogue with pauses"""
        speech_parts = []

        for qa in qa_pairs:
            speech_parts.append(f"Question: [pause short] {qa.question}")
            speech_parts.append(f"[pause medium] Answer: [pause short] {qa.answer}")
            speech_parts.append("[pause long]")

        return " ".join(speech_parts)

    def _format_simple_with_pauses(self, qa_pairs: List[QAPair]) -> str:
        """Simple format with strategic pauses"""
        speech_parts = []

        for qa in qa_pairs:
            speech_parts.append(qa.question)
            speech_parts.append("[pause medium]")
            speech_parts.append(qa.answer)
            speech_parts.append("[pause long]")

        return " ".join(speech_parts)

    # Utility methods for reusability
    def get_qa_summary(self, qa_pairs: List[QAPair]) -> Dict[str, int]:
        """
        Get summary statistics about extracted Q&A pairs

        Returns:
            Dictionary with summary stats
        """
        total_questions = len(qa_pairs)
        avg_question_length = (
            sum(len(qa.question.split()) for qa in qa_pairs) / total_questions
            if total_questions > 0
            else 0
        )
        avg_answer_length = (
            sum(len(qa.answer.split()) for qa in qa_pairs) / total_questions
            if total_questions > 0
            else 0
        )

        return {
            "total_pairs": total_questions,
            "avg_question_words": round(avg_question_length, 1),
            "avg_answer_words": round(avg_answer_length, 1),
            "estimated_speech_minutes": round(
                (avg_question_length + avg_answer_length) * total_questions / 150, 1
            ),  # 150 WPM average
        }

    def filter_qa_pairs(
        self,
        qa_pairs: List[QAPair],
        min_answer_words: int = 5,
        max_answer_words: Optional[int] = None,
    ) -> List[QAPair]:
        """
        Filter Q&A pairs based on criteria

        Args:
            qa_pairs: List of Q&A pairs to filter
            min_answer_words: Minimum words in answer
            max_answer_words: Maximum words in answer (optional)

        Returns:
            Filtered list of Q&A pairs
        """
        filtered = []

        for qa in qa_pairs:
            answer_word_count = len(qa.answer.split())

            if answer_word_count >= min_answer_words:
                if max_answer_words is None or answer_word_count <= max_answer_words:
                    filtered.append(qa)

        return filtered
