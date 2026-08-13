from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Removes query parameters and fragments from the URL to keep it unique.
    Example: https://avito.ru/product_id?context -> https://avito.ru/product_id
    """
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
