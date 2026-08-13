from dataclasses import dataclass, asdict
import decimal
from typing import Optional, Type

from src.scrapers.engine.base import ConnectingEngine
from src.scrapers.scraper.base import BaseScraper


@dataclass(frozen=True)
class SiteConfig:
    """
    Universal configuration describing the scraping rules
    for any supported website.
    """
    domains: tuple[str, ...]
    engine_cls: Type[ConnectingEngine]
    scraper_cls: Type[BaseScraper]
    wait_selectors: dict[str, list[str]]
    selectors: dict[str, list[str]]
    catch_waiting_errors: bool = False
    catch_extraction_errors: bool = False


@dataclass(frozen=True)
class ScrapedProductData:
    """
    Immutable data transfer object (DTO) representing
    the standardized result of a successful web scraping execution.
    """
    title: Optional[str]
    price: Optional[decimal.Decimal]
    description: Optional[str]
    photo: Optional[str]
    url: str

    def to_dict(self) -> dict:
        """Helper method to easily convert the dataclass to a standard dictionary."""
        return asdict(self)
