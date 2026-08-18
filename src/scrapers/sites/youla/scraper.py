import re
from typing import Optional

from src.scrapers.scraper.base import BaseScraper


class YoulaScraper(BaseScraper):
    """
    Extracts product information from an Youla document.
    """

    async def extract_title(self) -> Optional[str]:
        for selector in self.get_selectors("title"):
            value = await self.document.text(selector)

            if value:
                return value

        return None

    async def extract_price(self) -> Optional[int]:
        for selector in self.get_selectors("price"):
            value = await self.document.text(selector)

            if not value:
                continue

            return self._parse_price(value)

        return None

    async def extract_description(self) -> Optional[str]:
        for selector in self.get_selectors("description"):
            value = await self.document.text(selector)

            if value:
                return value

        return None

    async def extract_photo(self) -> Optional[str]:
        for selector in self.get_selectors("photo"):
            value = await self.document.attribute(selector, "data-src")
            if value and not value.startswith("data:"):
                return value

            value = await self.document.attribute(selector, "src")
            if value and not value.startswith("data:"):
                return value

        return None

    @staticmethod
    def _parse_price(value: str) -> Optional[int]:
        digits = re.sub(
            r"\D",
            "",
            value,
        )

        if not digits:
            return None

        return int(digits)
