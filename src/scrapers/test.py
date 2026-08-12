import asyncio
import sys
import logging
from src.scrapers.factory import ScraperFactory

# Setup logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("test_runner")


async def test_scraper(url: str):
    logger.info(f"Initializing scraping pipeline for: {url}")
    try:
        async with ScraperFactory.create(url) as pipeline:
            logger.info("Connection established, running pipeline...")
            result = await pipeline.run()

            logger.info("Scraping completed. Results:")
            for field, value in result.items():
                logger.info(f"  - {field}: {value}")

    except Exception as e:
        logger.error(f"Critical error during testing: {e}", exc_info=True)


if __name__ == "__main__":
    test_url = "https://www.avito.ru/perm/chasy_i_ukrasheniya/vintazhnye_chasy_chayka_8307111163?context=H4sIAAAAAAAA_wE6AMX_YToxOntzOjE6IngiO3M6MzY6IjQ1NTlhMTcxYWM4ZWI5ODJjNTljZTEzMzQ3MDNlNGE1Y2I2NiI7fX01h746AAAA"
    if len(sys.argv) > 1:
        test_url = sys.argv[1]

    asyncio.run(test_scraper(test_url))
