"""Input validation utilities."""

from typing import Optional

from pydantic import HttpUrl, ValidationError

from src.phishing.utils.logging_config import get_logger

logger = get_logger(__name__)


class URLValidationError(Exception):
    """Raised when URL validation fails."""

    pass


class ValidationResult:
    """Result of URL validation."""

    def __init__(self, is_valid: bool, url: Optional[str] = None, error: Optional[str] = None):
        """
        Initialize validation result.

        Args:
            is_valid: Whether validation passed
            url: Validated URL (if valid)
            error: Error message (if invalid)
        """
        self.is_valid = is_valid
        self.url = url
        self.error = error

    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid


def validate_url(url: str, strict: bool = True) -> str:
    """
    Validate and normalize a URL.

    Args:
        url: URL string to validate
        strict: Use strict validation (recommended for production)

    Returns:
        Validated URL string

    Raises:
        URLValidationError: If the URL is invalid
    """
    if not url or not isinstance(url, str):
        raise URLValidationError("URL must be a non-empty string")

    url = url.strip()

    if len(url) < 5:
        raise URLValidationError("URL too short")

    if len(url) > 2048:
        raise URLValidationError("URL too long (max 2048 characters)")

    # Check for basic URL structure
    if not any(url.startswith(proto) for proto in ["http://", "https://", "ftp://"]):
        url = "http://" + url

    if strict:
        try:
            # Use Pydantic's HttpUrl for strict validation
            validated = HttpUrl(url)
            return str(validated)
        except ValidationError as e:
            raise URLValidationError(f"Invalid URL format: {e.error_count()} validation error(s)") from e
        except Exception as e:
            raise URLValidationError(f"Invalid URL: {str(e)}") from e
    else:
        # Basic validation
        try:
            HttpUrl(url)
            return url
        except Exception as e:
            raise URLValidationError(f"Invalid URL: {str(e)}") from e


def validate_batch_urls(urls: list, max_batch_size: int = 100) -> tuple:
    """
    Validate a batch of URLs.

    Args:
        urls: List of URL strings
        max_batch_size: Maximum batch size

    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    if not isinstance(urls, list):
        raise URLValidationError("URLs must be a list")

    if len(urls) > max_batch_size:
        raise URLValidationError(f"Batch size exceeds limit ({max_batch_size})")

    valid_urls = []
    invalid_urls = []

    for idx, url in enumerate(urls):
        try:
            valid_url = validate_url(url)
            valid_urls.append(valid_url)
        except URLValidationError as e:
            invalid_urls.append({"index": idx, "url": url, "error": str(e)})
            logger.warning(f"Invalid URL at index {idx}: {str(e)}")

    return valid_urls, invalid_urls
