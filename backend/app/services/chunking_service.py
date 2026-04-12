# Document chunking service
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """Handles document chunking with overlaps"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_text(self, text: str, preserve_structure: bool = True) -> List[str]:
        """
        Split text into chunks with overlapping boundaries.

        Args:
            text: Raw document text
            preserve_structure: If True, tries to preserve document structure

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            raise ValueError("Empty text provided")

        # Clean text: remove excessive whitespace
        text = " ".join(text.split())

        # Split into chunks
        chunks = self.text_splitter.split_text(text)

        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks

    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (average 4 chars per token).
        For production, use proper tokenizer.
        """
        return len(text) // 4
