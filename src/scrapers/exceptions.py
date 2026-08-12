class ScraperError(Exception):
    """Base exception for scraper-related errors."""


class UnsupportedUrlError(ScraperError):
    """Raised when no scraper configuration matches the requested URL."""


class EngineError(ScraperError):
    """Raised when a connecting engine fails to obtain a document."""


class DocumentError(ScraperError):
    """Raised when a document cannot provide requested data."""


class ParsingError(ScraperError):
    """Raised when a parser fails to prepare a document."""


class ExtractionError(ScraperError):
    """Raised when a scraper fails to extract required data."""
