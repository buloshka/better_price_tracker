from abc import ABC, abstractmethod

from src.scrapers.document.base import Document


class ConnectingEngine(ABC):
    """
    Defines a strategy for establishing a connection and retrieving a document.

    Engines are responsible only for the transport/retrieval layer.
    They must not contain site-specific extraction logic.
    """

    async def __aenter__(self) -> "ConnectingEngine":
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self.close()

    @abstractmethod
    async def start(self) -> None:
        """Initialize engine resources."""
        raise NotImplementedError

    @abstractmethod
    async def connect(self, url: str) -> Document:
        """Retrieve a document from the specified URL."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Release engine resources."""
        raise NotImplementedError
