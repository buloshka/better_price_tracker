from pydantic import BaseModel, EmailStr, Field, ConfigDict, HttpUrl
from typing import Optional, Annotated
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    email: EmailStr


class UserAuthData(UserBase):
    password: Annotated[str, Field(min_length=6, max_length=64)]


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRegisterResponse(UserResponse):
    telegram_id: Annotated[Optional[int], Field(gt=0)] = None
    telegram_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductCreate(BaseModel):
    url: HttpUrl
    target_price: Annotated[Decimal, Field(gt=0)]


class ProductResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    url: str
    target_price: Decimal
    current_price: Optional[Decimal] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
