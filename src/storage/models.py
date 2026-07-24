from sqlalchemy import String, BigInteger, Text, ForeignKey, Numeric, func
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from typing import Annotated, TypeVar, Any, Optional

import datetime
import decimal


T = TypeVar('T', bound=Any)
PrimaryKey = Annotated[
    T,
    mapped_column(primary_key=True, autoincrement=True)
]
Timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
    )
]


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[PrimaryKey[int]]
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    telegram_id: Mapped[Optional[str]] = mapped_column(BigInteger, nullable=True, unique=True, index=True)
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
