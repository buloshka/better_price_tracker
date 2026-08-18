from src.scrapers.config import SiteConfig
from src.scrapers.engine.playwright import PlaywrightEngine
from src.scrapers.sites.youla.scraper import YoulaScraper


YOULA_CONFIG = SiteConfig(
    domains=(
        "youla.ru",
        "www.youla.ru",
    ),

    engine_cls=PlaywrightEngine,
    scraper_cls=YoulaScraper,

    wait_selectors={
        "title": ["[data-test-block='ProductCaption']"],
    },

    selectors={
        "title": ["[data-test-block='ProductCaption']"],
        "price": ["[data-test-component='Price']"],
        "description": ["[data-test-component='DescriptionList'] p"],
        "photo": [
            "[data-test-component='ProductGallery'] img:first-of-type",
        ],
    },

    catch_waiting_errors=True,
    catch_extraction_errors=True,
)
