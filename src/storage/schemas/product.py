import datetime
import decimal
import re
import uuid
from typing import Annotated, Optional
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError


SUPPORTED_URLS = re.compile(r"^https?://(www\.)?(avito\.ru|youla\.ru)/.*")


class ProductGet(BaseModel):
    """Schema for returning global product data."""
    id: Annotated[int, Field(title="Product ID")]
    url: Annotated[str, Field(title="Normalized Product URL")]
    title: Annotated[
        Optional[str],
        Field(default=None, title="Product Title")
    ]
    description: Annotated[
        Optional[str],
        Field(default=None, title="Description")
    ]
    image_url: Annotated[
        Optional[str],
        Field(default=None, title="Image CDN URL")
    ]
    current_price: Annotated[
        Optional[decimal.Decimal],
        Field(default=None, title="Current Price")
    ]
    last_checked_at: Annotated[
        Optional[datetime.datetime],
        Field(default=None, title="Last Checked Timestamp")
    ]
    created_at: Annotated[datetime.datetime, Field(title="Created At")]

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Schema for internal product creation inside the database.
    Populated by the service layer using ScrapedProductData from the scraper.
    """
    url: Annotated[str, Field(title="Normalized Product URL")]
    title: Annotated[
        Optional[str],
        Field(default=None, max_length=255, title="Product Title")
    ]
    description: Annotated[
        Optional[str],
        Field(default=None, title="Product Description")
    ]
    image_url: Annotated[
        Optional[str],
        Field(default=None, title="Image CDN URL")
    ]
    current_price: Annotated[
        Optional[decimal.Decimal],
        Field(default=None, gt=0, title="Initial Scraped Price")
    ]
    last_checked_at: Annotated[
        Optional[datetime.datetime],
        Field(default=None, title="Initial Check Timestamp")
    ]

    model_config = ConfigDict(from_attributes=True)


class UserProductCreate(BaseModel):
    """
    Schema for incoming user request to track a product.
    Accepts raw URL and user-defined target price.
    """
    url: Annotated[
        str,
        Field(
            title="Product URL",
            description="Must be a valid Avito or Youla product item link"
        )
    ]
    target_price: Annotated[
        decimal.Decimal,
        Field(
            gt=0,
            max_digits=10,
            decimal_places=2,
            title="Target Price",
            description="The price threshold at which user wants to receive notifications"
        )
    ]

    @field_validator('url', mode='before')
    @classmethod
    def validate_and_normalize_url(cls, url: str) -> str:
        """Validates that URL belongs to a supported site and cuts off analytics/query params."""
        clean_url = url.strip()

        if not SUPPORTED_URLS.match(clean_url):
            raise PydanticCustomError(
                'no_field_error',
                'URL must be a valid link from avito.ru or youla.ru'
            )

        parsed = urlparse(clean_url)
        normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        return normalized


class UserProductGet(BaseModel):
    """Schema for returning user subscription info including the product data itself."""
    id: Annotated[int, Field(title="Subscription ID")]
    user_id: Annotated[
        uuid.UUID,
        Field(title="User ID reference")
    ]
    product_id: Annotated[
        int,
        Field(title="Product ID reference")
    ]
    product: Annotated[
        ProductGet,
        Field(title="Associated Product Details")
    ]
    target_price: Annotated[
        decimal.Decimal,
        Field(title="User Target Price")
    ]
    old_price: Annotated[
        Optional[decimal.Decimal],
        Field(default=None)
    ]
    is_notification_enabled: Annotated[
        bool,
        Field(title="Notification Status")
    ]
    created_at: Annotated[
        datetime.datetime,
        Field(title="Created At")
    ]

    model_config = ConfigDict(from_attributes=True)


class PriceHistoryGet(BaseModel):
    """Schema for returning a specific point in a product's price history chart."""
    id: Annotated[
        int,
        Field(title="History Log ID")
    ]
    product_id: Annotated[
        int,
        Field(title="Product ID reference")
    ]
    price: Annotated[
        decimal.Decimal,
        Field(title="Historical Price")
    ]
    recorded_at: Annotated[
        datetime.datetime,
        Field(title="Recorded At")
    ]

    model_config = ConfigDict(from_attributes=True)
