"""Feature extraction from URLs for ML model inference."""

import re
import socket
from typing import List, Optional
from urllib.parse import urlparse

import tldextract

from src.phishing.config.settings import settings
from src.phishing.utils.logging_config import get_logger

logger = get_logger(__name__)

# Feature extraction constants
SHORTENING_SERVICES = r"bit\.ly|goo\.gl|tinyurl|ow\.ly|t\.co|is\.gd|cli\.gs|short\.link|bitly|tinyurl"
PHISHING_KEYWORDS = r"confirm|verify|account|update|secure|alert|action"
NUM_FEATURES = 30


class FeatureExtractionError(Exception):
    """Raised when feature extraction fails."""

    pass


def extract_ip_address(url: str) -> int:
    """
    Check if URL uses IP address instead of domain.

    Args:
        url: URL to check

    Returns:
        -1 if IP address found, 1 if domain name
    """
    ip_pattern = r"(([0-9]{1,3}\.){3}[0-9]{1,3})"
    return -1 if re.search(ip_pattern, url) else 1


def extract_url_length(url: str) -> int:
    """
    Analyze URL length (longer URLs more likely phishing).

    Args:
        url: URL to analyze

    Returns:
        -1 if very long (>=75), 0 if medium (>=54), 1 if short
    """
    length = len(url)
    if length >= 75:
        return -1
    elif length >= 54:
        return 0
    else:
        return 1


def extract_shortening_service(url: str) -> int:
    """
    Check if URL uses shortening service.

    Args:
        url: URL to check

    Returns:
        -1 if shortening service found, 1 if not
    """
    return -1 if re.search(SHORTENING_SERVICES, url, re.IGNORECASE) else 1


def extract_at_symbol(url: str) -> int:
    """
    Check for @ symbol (often used to obfuscate domain).

    Args:
        url: URL to check

    Returns:
        -1 if @ found, 1 if not
    """
    return -1 if "@" in url else 1


def extract_double_slash(url: str) -> int:
    """
    Check for multiple //.

    Args:
        url: URL to check

    Returns:
        -1 if multiple // found, 1 if not
    """
    return -1 if url.count("//") > 1 else 1


def extract_hyphen_domain(url: str) -> int:
    """
    Check for hyphen in domain (often used in phishing).

    Args:
        url: URL to check

    Returns:
        -1 if hyphen in domain, 1 if not
    """
    try:
        domain = urlparse(url).netloc
        return -1 if "-" in domain else 1
    except Exception:
        return 0


def extract_subdomain_count(url: str) -> int:
    """
    Count subdomains (too many indicates suspicious).

    Args:
        url: URL to check

    Returns:
        -1 if many subdomains (>1), 0 if one, 1 if none
    """
    try:
        extracted = tldextract.extract(url)
        subdomain = extracted.subdomain
        if not subdomain:
            return 1
        num_dots = subdomain.count(".") + 1
        if num_dots > 1:
            return -1
        else:
            return 0
    except Exception:
        return 0


def extract_https_in_domain(url: str) -> int:
    """
    Check for 'https' token in domain (obfuscation technique).

    Args:
        url: URL to check

    Returns:
        -1 if 'https' in domain, 1 if not
    """
    try:
        domain = urlparse(url).netloc
        return -1 if "https" in domain.lower() else 1
    except Exception:
        return 0


def extract_https_protocol(url: str) -> int:
    """
    Check if URL uses HTTPS protocol.

    Args:
        url: URL to check

    Returns:
        1 if HTTPS, -1 if HTTP
    """
    return 1 if url.startswith("https://") else -1


def extract_dns_lookup(url: str, timeout: Optional[float] = None) -> int:
    """
    Validate domain by DNS lookup.

    Args:
        url: URL to check
        timeout: Lookup timeout in seconds

    Returns:
        1 if domain resolves, -1 if not
    """
    if not settings.dns_lookup_enabled:
        return 0

    if timeout is None:
        timeout = settings.dns_lookup_timeout

    try:
        domain = urlparse(url).netloc
        if not domain:
            return -1

        # Remove port if present
        domain = domain.split(":")[0]

        # Set socket timeout
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(domain)
        return 1
    except socket.timeout:
        logger.warning(f"DNS lookup timeout for {domain}")
        return 0
    except (socket.gaierror, socket.error, Exception):
        return -1
    finally:
        socket.setdefaulttimeout(None)


def extract_phishing_keywords(url: str) -> int:
    """
    Check for common phishing keywords in URL.

    Args:
        url: URL to check

    Returns:
        -1 if phishing keywords found, 1 if not
    """
    return -1 if re.search(PHISHING_KEYWORDS, url, re.IGNORECASE) else 1


def extract_mailto_check(url: str) -> int:
    """
    Check for mailto: prefix (suspicious in certain contexts).

    Args:
        url: URL to check

    Returns:
        -1 if mailto found, 1 if not
    """
    return -1 if re.search(r"mailto:", url, re.IGNORECASE) else 1


def extract_features_from_url(url: str) -> List[int]:
    """
    Extract feature vector from URL.

    Args:
        url: URL to extract features from

    Returns:
        Feature vector (list of integers, padded to NUM_FEATURES)

    Raises:
        FeatureExtractionError: If extraction fails
    """
    try:
        if not url or not isinstance(url, str):
            raise FeatureExtractionError("URL must be a non-empty string")

        features: List[int] = []

        # Extract all features
        features.append(extract_ip_address(url))
        features.append(extract_url_length(url))
        features.append(extract_shortening_service(url))
        features.append(extract_at_symbol(url))
        features.append(extract_double_slash(url))
        features.append(extract_hyphen_domain(url))
        features.append(extract_subdomain_count(url))
        features.append(extract_https_in_domain(url))
        features.append(extract_https_protocol(url))
        features.append(extract_phishing_keywords(url))
        features.append(extract_mailto_check(url))
        features.append(extract_dns_lookup(url))

        # Placeholder features (for model compatibility)
        placeholder_count = NUM_FEATURES - len(features)
        features.extend([0] * placeholder_count)

        # Ensure exact size
        features = features[:NUM_FEATURES]

        logger.debug(f"Extracted {len(features)} features from URL")

        return features

    except Exception as e:
        logger.error(f"Feature extraction failed: {str(e)}", exc_info=True)
        raise FeatureExtractionError(f"Failed to extract features: {str(e)}") from e


def get_feature_names() -> List[str]:
    """Get human-readable feature names."""
    return [
        "IP Address",
        "URL Length",
        "Shortening Service",
        "@ Symbol",
        "Double Slash",
        "Hyphen in Domain",
        "Subdomain Count",
        "HTTPS in Domain",
        "HTTPS Protocol",
        "Phishing Keywords",
        "Mailto Check",
        "DNS Lookup",
        *[f"Feature {i+13}" for i in range(NUM_FEATURES - 12)],
    ]
