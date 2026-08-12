from src.scrapers.config import SiteConfig
from src.scrapers.engine.playwright import PlaywrightEngine
from src.scrapers.sites.avito.scraper import AvitoScraper


AVITO_CONFIG = SiteConfig(
    domains=(
        "avito.ru",
        "www.avito.ru",
    ),

    engine_cls=PlaywrightEngine,
    scraper_cls=AvitoScraper,

    wait_selectors={
        "title": ["h1"],
    },

    selectors={
        "title": ["h1"],
        "price": ["[data-marker='item-view/item-price']"],
        "description": ["[data-marker='item-view/item-description']"],
        "photo": [
            "[data-marker='item-view/gallery-img'] img",
            "img",
        ],
    },

    catch_waiting_errors=True,
    catch_extraction_errors=True,
)
