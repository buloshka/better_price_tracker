from dataclasses import dataclass, asdict
import decimal
from typing import Optional


@dataclass(frozen=True)
class ScrapedProductData:
    """
    Immutable data transfer object (DTO) representing
    the standardized result of a successful web scraping execution.
    """
    title: Optional[str]
    price: Optional[decimal.Decimal]
    description: Optional[str]
    photo: Optional[str]
    url: str

    def to_dict(self) -> dict:
        return asdict(self)
