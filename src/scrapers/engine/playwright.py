import asyncio
import sys
import logging
import random
from typing import Optional
from playwright.async_api import async_playwright, Playwright, Browser
from playwright_stealth import Stealth

from src.scrapers.document.httpx import HttpxDocument
from src.scrapers.engine.base import ConnectingEngine
from src.scrapers.exceptions import EngineError


logger = logging.getLogger("scrapers.engine.playwright")


class PlaywrightEngine(ConnectingEngine):
    """
    Engine based on Playwright + Playwright-Stealth + Manual Evasions + Proxy Support
    to bypass strict anti-bot systems like Avito and Ozon.
    """

    def __init__(
            self,
            *,
            headless: bool = True,
            timeout: float = 30000.0,
            proxy: Optional[dict[str, str]] = None  # Добавили поддержку прокси
    ):
        self.headless = headless
        self.timeout = timeout
        self.proxy = proxy

        self._playwright_cm = None
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    async def _human_delay(self, min_sec: float = 1.5, max_sec: float = 4.0):
        """Generates a random human-like delay to bypass rate-limiting."""
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Applying human-like delay for {delay:.2f} seconds...")
        await asyncio.sleep(delay)

    async def start(self) -> None:
        if self._browser is not None:
            return

        if sys.platform == 'win32':
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            except Exception as e:
                logger.debug(f"Loop policy already set or could not be modified: {e}")

        logger.info("Launching Chromium instance with enhanced Stealth configurations...")
        try:
            self._playwright_cm = Stealth().use_async(async_playwright())
            self._playwright = await self._playwright_cm.__aenter__()

            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-gpu",
                ]
            )
            logger.info("Browser session successfully opened")
        except Exception as exc:
            logger.error(f"Failed to boot Playwright interface: {exc}")
            raise EngineError("Failed to start Playwright browser.") from exc

    async def connect(self, url: str) -> HttpxDocument:
        if self._browser is None:
            raise EngineError("PlaywrightEngine has not been started. Use it as an async context manager.")

        logger.info(f"Opening target endpoint inside browser window -> {url}")

        width = random.randint(1366, 1920)
        height = random.randint(768, 1080)

        context_kwargs = {
            "viewport": {"width": width, "height": height},
            "locale": "ru-RU",
            "timezone_id": "Europe/Moscow",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "java_script_enabled": True,
            "ignore_https_errors": True
        }

        if self.proxy:
            logger.info(f"Applying proxy settings for this connection: {self.proxy.get('server')}")
            context_kwargs["proxy"] = self.proxy

        context = await self._browser.new_context(**context_kwargs)

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { 
                get: () => undefined 
            });
            Object.defineProperty(navigator, 'plugins', { 
                get: () => [1, 2, 3, 4, 5] 
            });
        """)

        page = await context.new_page()
        page.set_default_timeout(self.timeout)
        page.set_default_navigation_timeout(self.timeout)

        try:
            response = await page.goto(url, wait_until="domcontentloaded")
            await self._human_delay(2.0, 4.5)

            status_code = response.status if response else 200
            html_content = await page.content()
            final_url = page.url

            logger.info(f"Webpage content fully fetched. Status: {status_code} | HTML Length: {len(html_content)}")

            if status_code == 429:
                logger.error("Rate limit hit (Status 429). Proxy IP might be flagged or you need to switch IPs.")
            elif status_code == 439:
                logger.error("Target platform returned status 439 (WAF Block).")

            return HttpxDocument(
                url=final_url,
                status_code=status_code,
                html=html_content
            )

        except Exception as exc:
            logger.error(f"Exception triggered while rendering webpage {url}: {exc}")
            raise EngineError(f"Playwright failed to retrieve URL: {url}") from exc
        finally:
            await page.close()
            await context.close()

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright_cm is not None:
            await self._playwright_cm.__aexit__(None, None, None)
            self._playwright_cm = None
            self._playwright = None

        logger.info("PlaywrightEngine stopped successfully, resources detached")
