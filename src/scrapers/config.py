from dataclasses import dataclass
from typing import Type

from src.scrapers.engine.base import ConnectingEngine
from src.scrapers.scraper import BaseScraper


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
