import decimal
import logging

from abc import ABC, abstractmethod
from typing import Optional

from src.scrapers.models import ScrapedProductData
from src.scrapers.document.base import Document
from src.scrapers.exceptions import ExtractionError


logger = logging.getLogger("scrapers.scraper")


class BaseScraper(ABC):
    def __init__(
            self,
            *,
            document: Document,
            selectors: Optional[dict[str, list[str]]] = None,
            catch_errors: bool = False
    ):
        self.document = document
        self.selectors = selectors or {}
        self.catch_errors = catch_errors

    async def extract(self) -> ScrapedProductData:
        """
        Extracts all standard fields from the document
        and returns a strongly typed ScrapedProductData object.
        """
        temp_result = {}
        fields = ("title", "price", "description", "photo", "url")

        logger.info(f"Starting field extraction for URL: {self.document.url}")

        for field_name in fields:
            try:
                method = getattr(self, f"extract_{field_name}")
                logger.debug(f"Extracting field '{field_name}'...")

                value = await method()

                if value is None:
                    logger.warning(f"Field '{field_name}' not found (returned None)")
                else:
                    logger.info(f"Field '{field_name}' successfully extracted")

                temp_result[field_name] = value

            except Exception as exc:
                if not self.catch_errors:
                    logger.error(f"Critical error extracting field '{field_name}': {exc}")
                    raise ExtractionError(f"Failed to extract field '{field_name}'.") from exc

                logger.warning(f"Error extracting field '{field_name}', returning None. Error: {exc}")
                temp_result[field_name] = None

        if temp_result["price"] is not None:
            try:
                temp_result["price"] = decimal.Decimal(str(temp_result["price"]))
            except (ValueError, decimal.InvalidOperation):
                logger.warning(f"Failed to convert price '{temp_result['price']}' to Decimal, setting to None")
                temp_result["price"] = None

        return ScrapedProductData(
            title=temp_result["title"],
            price=temp_result["price"],
            description=temp_result["description"],
            photo=temp_result["photo"],
            url=temp_result["url"]
        )

    def get_selectors(self, field_name: str) -> list[str]:
        return self.selectors.get(field_name, [])

    @abstractmethod
    async def extract_title(self) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def extract_price(self) -> Optional[int]:
        raise NotImplementedError

    @abstractmethod
    async def extract_description(self) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def extract_photo(self) -> Optional[str]:
        raise NotImplementedError

    async def extract_url(self) -> str:
        return self.document.url
