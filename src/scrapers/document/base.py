from abc import ABC, abstractmethod
from typing import Optional


class Document(ABC):
    """
    Represents a retrieved web document independently of the underlying engine.

    A document may be backed by an HTTP response, a browser page,
    a cached HTML document, or any other retrieval mechanism.
    """

    @property
    @abstractmethod
    def url(self) -> str:
        """Return the final document URL."""
        raise NotImplementedError

    @property
    @abstractmethod
    def status_code(self) -> Optional[int]:
        """Return the HTTP status code when available."""
        raise NotImplementedError

    @abstractmethod
    async def content(self) -> str:
        """Return the document HTML content."""
        raise NotImplementedError

    @abstractmethod
    async def text(self, selector: str) -> Optional[str]:
        """Extract text from the first matching element."""
        raise NotImplementedError

    @abstractmethod
    async def attribute(
        self,
        selector: str,
        name: str,
    ) -> Optional[str]:
        """Extract an attribute from the first matching element."""
        raise NotImplementedError

    @abstractmethod
    async def wait_for(
        self,
        selectors: list[str],
    ) -> None:
        """
        Wait until at least one of the provided selectors is available.

        The exact implementation depends on the document backend.
        """
        raise NotImplementedError

    async def close(self) -> None:
        """
        Release document-specific resources.

        Most static documents do not need explicit cleanup.
        Browser-backed documents may override this method.
        """
