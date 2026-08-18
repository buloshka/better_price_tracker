from src.scrapers.models import ScrapedProductData
from src.scrapers.parser.base import BaseParser
from src.scrapers.scraper.base import BaseScraper


class ScrapingPipeline:
    """
    Coordinates engine, parser, and scraper lifecycles.

    The pipeline is the public runtime interface of the scraping subsystem.
    """

    def __init__(
        self,
        *,
        parser: BaseParser,
        scraper_cls: type[BaseScraper],
        scraper_selectors: dict[str, list[str]],
        catch_extraction_errors: bool = False,
    ):
        self.parser = parser

        self.scraper_cls = scraper_cls
        self.scraper_selectors = scraper_selectors
        self.catch_extraction_errors = catch_extraction_errors

        self._scraper: BaseScraper | None = None

    async def __aenter__(self) -> "ScrapingPipeline":
        if self.parser.engine is None:
            raise RuntimeError(
                "Parser has no connecting engine."
            )

        await self.parser.engine.start()

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        if self.parser.engine is not None:
            await self.parser.engine.close()

    async def run(self) -> ScrapedProductData:
        document = await self.parser.parse()

        self._scraper = self.scraper_cls(
            document=document,
            selectors=self.scraper_selectors,
            catch_errors=self.catch_extraction_errors,
        )

        try:
            return await self._scraper.extract()
        finally:
            await document.close()
