from typing import Optional
import logging
from src.scrapers.document.base import Document
from src.scrapers.engine.base import ConnectingEngine
from src.scrapers.exceptions import ParsingError


logger = logging.getLogger("scrapers.parser")


class BaseParser:
    """
    Orchestrates document retrieval through a connecting engine.

    The parser does not know how the engine establishes a connection.
    """

    def __init__(self, *, url: str):
        self.url = url
        self._engine: Optional[ConnectingEngine] = None
        self._wait_selectors: dict[str, list[str]] = {}
        self._catch_waiting_errors = False
        self._document: Optional[Document] = None

    @property
    def engine(self) -> Optional[ConnectingEngine]:
        return self._engine

    def with_engine(self, engine: ConnectingEngine) -> "BaseParser":
        self._engine = engine
        return self

    def with_waiting(
            self,
            selectors: Optional[dict[str, list[str]]] = None,
            *,
            catch_errors: bool = False,
    ) -> "BaseParser":
        if selectors is not None:
            self._wait_selectors = selectors
        self._catch_waiting_errors = catch_errors
        return self

    async def parse(self) -> Document:
        if self._engine is None:
            raise ParsingError("No connecting engine has been configured.")

        try:
            self._document = await self._engine.connect(self.url)
            await self._wait_for_required_fields()
            return self._document

        except Exception as exc:
            if isinstance(exc, ParsingError):
                raise
            raise ParsingError(f"Failed to parse URL: {self.url}") from exc

    async def _wait_for_required_fields(self) -> None:
        if self._document is None:
            raise ParsingError("Document has not been initialized.")

        for field_name, selectors in self._wait_selectors.items():
            if not selectors:
                continue

            try:
                logger.debug(f"Waiting for required field '{field_name}' using selectors: {selectors}")
                await self._document.wait_for(selectors)
                logger.info(f"Required field '{field_name}' successfully detected on the page.")
            except Exception as exc:
                if not self._catch_waiting_errors:
                    logger.error(f"Failed waiting for required field '{field_name}': {exc}")
                    raise ParsingError(f"Failed waiting for field '{field_name}'.") from exc
                logger.warning(f"Timeout waiting for field '{field_name}' (ignored by config): {exc}")
