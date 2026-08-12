from typing import Optional

from bs4 import BeautifulSoup

from src.scrapers.document.base import Document


class HttpxDocument(Document):
    """
    Document implementation backed by an HTTP response.
    """

    def __init__(
        self,
        *,
        url: str,
        status_code: int,
        html: str,
    ):
        self._url = url
        self._status_code = status_code
        self._html = html

        self._soup: Optional[BeautifulSoup] = None

    @property
    def url(self) -> str:
        return self._url

    @property
    def status_code(self) -> int:
        return self._status_code

    async def content(self) -> str:
        return self._html

    def _get_soup(self) -> BeautifulSoup:
        if self._soup is None:
            self._soup = BeautifulSoup(
                self._html,
                "html.parser",
            )

        return self._soup

    async def text(self, selector: str) -> Optional[str]:
        element = self._get_soup().select_one(selector)

        if element is None:
            return None

        return element.get_text(
            separator=" ",
            strip=True,
        )

    async def attribute(
        self,
        selector: str,
        name: str,
    ) -> Optional[str]:
        element = self._get_soup().select_one(selector)

        if element is None:
            return None

        value = element.get(name)

        if value is None:
            return None

        return str(value)

    async def wait_for(
        self,
        selectors: list[str],
    ) -> None:
        """
        HTTP documents are static.

        There is no asynchronous DOM mutation to wait for.
        The method only checks whether one of the selectors exists.
        """

        if not selectors:
            return

        soup = self._get_soup()

        for selector in selectors:
            if soup.select_one(selector) is not None:
                return
