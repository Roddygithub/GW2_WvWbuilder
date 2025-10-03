"""Test utility functions."""

import random
import string
from urllib.parse import urlparse


def random_lower_string(length: int = 10) -> str:
    """Generate a random string of lowercase letters and digits.

    Args:
        length: Length of the string to generate.

    Returns:
        A random string of the specified length.
    """
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_email(domain: str = "example.com") -> str:
    """Generate a random email address.

    Args:
        domain: Domain to use for the email.

    Returns:
        A random email address.
    """
    return f"{random_lower_string()}@{domain}"


def random_url(scheme: str = "https", netloc: str = "example.com") -> str:
    """Generate a random URL.

    Args:
        scheme: URL scheme (http, https, etc.).
        netloc: Network location part (domain).

    Returns:
        A random URL.
    """
    path = "/".join(
        [""] + [random_lower_string(5) for _ in range(random.randint(1, 3))]
    )
    return f"{scheme}://{netloc}{path}"


def assert_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
