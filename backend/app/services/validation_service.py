# Input validation and guardrails
import re
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """Handles input validation and content masking"""

    # PII patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    @staticmethod
    def validate_file_type(filename: str, allowed_types: list) -> str:
        """
        Validate file extension.

        Args:
            filename: File name
            allowed_types: List of allowed extensions (e.g., ['pdf', 'csv'])

        Returns:
            Lowercased extension

        Raises:
            ValueError: If file type not allowed
        """
        file_extension = filename.split('.')[-1].lower()
        if file_extension not in allowed_types:
            raise ValueError(f"File type '{file_extension}' not allowed")
        return file_extension

    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> None:
        """
        Validate file size.

        Args:
            file_size: File size in bytes
            max_size: Maximum allowed size in bytes

        Raises:
            ValueError: If file exceeds max size
        """
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise ValueError(f"File exceeds maximum size of {max_mb}MB")

    @staticmethod
    def validate_query(query: str, max_length: int = 500) -> None:
        """
        Validate user query.

        Args:
            query: User query string
            max_length: Maximum query length

        Raises:
            ValueError: If query invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if len(query) > max_length:
            raise ValueError(f"Query exceeds maximum length of {max_length}")

    @staticmethod
    def mask_pii(text: str) -> str:
        """
        Mask personally identifiable information in text.

        Args:
            text: Text to mask

        Returns:
            Text with PII masked
        """
        # Mask emails
        text = ValidationService.EMAIL_PATTERN.sub("[EMAIL]", text)

        # Mask phone numbers
        text = ValidationService.PHONE_PATTERN.sub("[PHONE]", text)

        # Mask SSNs
        text = ValidationService.SSN_PATTERN.sub("[SSN]", text)

        return text

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough token estimation (average 4 chars per token).
        For production, use proper tokenizer like tiktoken.

        Args:
            text: Text to estimate tokens for

        Returns:
            Approximate token count
        """
        if not text:
            return 0
        # Conservative estimate: ~4 characters per token
        # Normalize whitespace first
        text = " ".join(text.split())
        return max(1, len(text) // 4)
