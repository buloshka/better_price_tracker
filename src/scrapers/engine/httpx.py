import logging
from typing import Optional
import httpx
from src.scrapers.document.httpx import HttpxDocument
from src.scrapers.engine.base import ConnectingEngine
from src.scrapers.exceptions import EngineError


logger = logging.getLogger("scrapers.engine.httpx")


class HttpxEngine(ConnectingEngine):
    """
    Enhanced HTTP engine featuring basic bot detection countermeasures.
    """

    def __init__(
            self,
            *,
            timeout: float = 20.0,
            headers: Optional[dict[str, str]] = None,
            follow_redirects: bool = True,
    ):
        self.timeout = timeout
        self.follow_redirects = follow_redirects

        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://google.com",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        self.headers = default_headers
        if headers:
            self.headers.update(headers)

        self._client: Optional[httpx.AsyncClient] = None

    async def start(self) -> None:
        if self._client is not None:
            return
        logger.debug("Launching AsyncClient with HTTP/2 protocol support")

        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
            follow_redirects=self.follow_redirects,
            http2=True
        )

    async def connect(self, url: str) -> HttpxDocument:
        if self._client is None:
            raise EngineError("HttpxEngine has not been started. Use it as an async context manager.")

        logger.info(f"Sending GET request -> {url}")
        try:
            response = await self._client.get(url)
            logger.info(
                f"Response received. Status: {response.status_code} | Protocol: {response.http_version} | HTML Length: {len(response.text)}"
            )

            if response.status_code == 439:
                logger.error("Resource blocked by Avito WAF (Code 439). Proxy setup or TLS fingerprinting required.")
            elif response.status_code != 200:
                logger.warning(f"Unexpected non-200 server response status: {response.status_code}")

            return HttpxDocument(
                url=str(response.url),
                status_code=response.status_code,
                html=response.text,
            )
        except httpx.HTTPError as exc:
            logger.error(f"Network error encountered during requesting {url}: {exc}")
            raise EngineError(f"Failed to retrieve URL: {url}") from exc

    async def close(self) -> None:
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None
        logger.debug("HttpxEngine successfully shut down")
