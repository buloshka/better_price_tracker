import datetime
import decimal
import uuid
from typing import Annotated, Any, Optional, TypeVar

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


T = TypeVar('T', bound=Any)
PrimaryKey = Annotated[
    T,
    mapped_column(primary_key=True, autoincrement=True)
]
Timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
]


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[PrimaryKey[uuid.UUID]] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[Optional[str]] = mapped_column(BigInteger, nullable=True, unique=True, index=True)
    telegram_code: Mapped[Optional[int]] = mapped_column(nullable=True)
    is_gmail_verified: Mapped[bool] = mapped_column(default=False, nullable=False, server_default='false')
    is_tg_verified: Mapped[bool] = mapped_column(default=False, nullable=False, server_default='false')
    last_email_sent_at: Mapped[Optional[Timestamp]]
    created_at: Mapped[Timestamp]


class Products(Base):
    """
    Stores global product details extracted by scrapers.
    URLs are normalized, unique, and indexed.
    """
    __tablename__ = 'products'

    id: Mapped[PrimaryKey[int]]
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)  # Unique, clean URL
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Global tracking price state
    current_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    last_checked_at: Mapped[Optional[Timestamp]] = mapped_column(default=None, nullable=True)
    created_at: Mapped[Timestamp]

    __table_args__ = (
        CheckConstraint("current_price >= 0", name="check_current_price_is_positive"),
    )


class UsersProducts(Base):
    """
    The junction table (Many-to-Many) linking Users and Products.
    Stores user-specific tracking parameters (target price, notification rules).
    """
    __tablename__ = 'users_products'

    id: Mapped[PrimaryKey[int]]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete="CASCADE"), nullable=False)
    target_price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_notification_enabled: Mapped[bool] = mapped_column(default=True, nullable=False, server_default='true')
    created_at: Mapped[Timestamp]

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_user_product'),
        CheckConstraint("target_price > 0", name="check_target_price_is_positive"),
    )


class PriceHistory(Base):
    """
    Global price historical data logs tied to a unique Product,
    independent of user tracking lists.
    """
    __tablename__ = 'price_history'

    id: Mapped[PrimaryKey[int]] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete="CASCADE"), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    recorded_at: Mapped[Timestamp] = mapped_column(index=True)

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_historical_price_is_positive"),
    )
