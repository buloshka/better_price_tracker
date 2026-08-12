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

    id: Mapped[PrimaryKey[str]] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, autoincrement=False)
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
    __tablename__ = 'products'

    id: Mapped[PrimaryKey[int]]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    target_price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    current_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    last_checked_at: Mapped[Optional[Timestamp]] = mapped_column(default=None, nullable=True)
    created_at: Mapped[Timestamp]

    __table_args__ = (
        UniqueConstraint('user_id', 'url', name='unique_id_url'),
        CheckConstraint("current_price >= 0", name="check_current_price_is_more_than_zero"),
        CheckConstraint("target_price > 0", name="check_target_price_is_more_than_zero"),
    )


class PriceHistory(Base):
    __tablename__ = 'price_history'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete="CASCADE"))
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    recorded_at: Mapped[Timestamp] = mapped_column(index=True)

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_current_price_is_more_than_zero"),
    )
