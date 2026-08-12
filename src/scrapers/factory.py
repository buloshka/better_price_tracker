from urllib.parse import urlparse

from src.scrapers.engine.base import ConnectingEngine
from src.scrapers.parser.base import BaseParser
from src.scrapers.pipeline import ScrapingPipeline
from src.scrapers.config import SiteConfig
from src.scrapers.sites.avito.config import AVITO_CONFIG
from src.scrapers.exceptions import UnsupportedUrlError


class ScraperFactory:
    """
    Builds a complete scraping pipeline for a supported URL.
    """

    CONFIGS: tuple[SiteConfig, ...] = (
        AVITO_CONFIG,
    )

    @classmethod
    def get_config(
        cls,
        url: str,
    ) -> SiteConfig:
        hostname = urlparse(url).hostname

        if not hostname:
            raise UnsupportedUrlError(
                f"Invalid URL: {url}"
            )

        hostname = hostname.lower()

        for config in cls.CONFIGS:
            for domain in config.domains:
                if hostname == domain or hostname.endswith(
                    f".{domain}"
                ):
                    return config

        raise UnsupportedUrlError(
            f"The domain in URL '{url}' is not supported."
        )

    @classmethod
    def create(
        cls,
        url: str,
    ) -> ScrapingPipeline:
        config = cls.get_config(url)

        engine: ConnectingEngine = config.engine_cls()

        parser = (
            BaseParser(url=url)
            .with_engine(engine)
            .with_waiting(
                config.wait_selectors,
                catch_errors=config.catch_waiting_errors,
            )
        )

        return ScrapingPipeline(
            parser=parser,
            scraper_cls=config.scraper_cls,
            scraper_selectors=config.selectors,
            catch_extraction_errors=config.catch_extraction_errors,
        )
