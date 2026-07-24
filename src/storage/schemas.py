from pydantic import BaseModel, EmailStr, Field, ConfigDict, HttpUrl
from typing import Optional
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта пользователя")


class UserData(UserBase):
    password: str = Field(..., min_length=6, description="Пароль, минимум 6 символов")


class UserResponse(UserBase):
    id: int
    telegram_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductCreate(BaseModel):
    url: str = Field(HttpUrl, description="Ссылка на страницу товара")
    target_price: Decimal = Field(..., gt=0, description="Желаемая цена (должна быть > 0)")


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
