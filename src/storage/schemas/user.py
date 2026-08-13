import datetime
import re
import uuid
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

from src.storage.schemas import UserProductGet

ALL_LETTERS = re.compile(r"^[а-яА-ЯёЁa-zA-Z\-\ ]+$")
UNICODE_SPACES = re.compile(
    r"[\s\u00A0\u2000-\u2006\u2800\u3164\uFFA0\uFFFC]"
)


class UserGet(BaseModel):
    """
    Data transfer object (DTO) representing an account configuration
    and general meta-information returned from database select operations.
    """
    id: Annotated[
        Optional[uuid.UUID],
        Field(
            default=None, title='ID',
        ),
    ]
    name: Annotated[
        Optional[str],
        Field(
            default=None, title='Name'
        ),
    ]
    email: EmailStr
    telegram_id: Annotated[
        Optional[int],
        Field(
            default=None, title='Telegram ID'
        ),
    ]
    is_gmail_verified: Annotated[
        bool,
        Field(
            default=False, title='Account verify'
        )
    ]
    is_tg_verified: Annotated[
        bool,
        Field(
            default=False, title='Telegram verify'
        )
    ]
    products: Annotated[
        list[UserProductGet],
        Field(default_factory=list, title='Tracked Products Link')
    ]

    created_at: Annotated[
        Optional[datetime.datetime],
        Field(
            default=None, title='Created at'
        ),
    ]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Validation schema handling public payloads directed toward sign-up processing endpoints.
    Enforces strict regex constraints on credentials, formatting, and formatting characters.
    """
    id: Annotated[
        Optional[uuid.UUID],
        Field(
            default=None, title='ID',
            description='must be uuid.UUID type'
        ),
    ]
    name: Annotated[
        str,
        Field(
            min_length=2, max_length=255, title="Name",
            description='must contain only letters and be at least 2 characters long'
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            min_length=5, title='Email',
            description='must be a valid email address (e.g., user@example.com)'
        ),
    ]
    password: Annotated[
        str,
        Field(
            min_length=6, max_length=64, title='Password',
            description='must be at least 6 characters long and doesn\'t contain spaces'
        ),
    ]
    telegram_id: Annotated[
        Optional[int],
        Field(
            default=None, title='Telegram ID',
            description='must be at least 6 characters long or empty'
        ),
    ]
    is_gmail_verified: Annotated[
        bool,
        Field(
            default=False,
            description='is this user verified?',
        )
    ]
    is_tg_verified: Annotated[
        bool,
        Field(
            default=False,
            description='is user\'s telegram verified?',
        )
    ]

    @field_validator('name', mode='before')
    @classmethod
    def name_validator(cls, name: str) -> str:
        """Enforces that name contains only alphabetic characters and trims whitespace."""
        if not ALL_LETTERS.match(name):
            raise PydanticCustomError(
                'invalid_name',
                'must contain only letters and be at least 2 characters long'
            )
        return name.strip()

    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Verifies that the chosen password contains zero blank spaces or unicode gap symbols."""
        if re.search(UNICODE_SPACES, password.strip()):
            raise PydanticCustomError(
                'invalid_password',
                "must be at least 6 characters long and must not contain any spaces or blank characters"
            )
        return password.strip()

    @field_validator('telegram_id', mode='after')
    @classmethod
    def telegram_id_validator(cls, telegram_id: Optional[int]) -> Optional[int]:
        """Validates that a provided Telegram unique ID meets minimum numeric length standard."""
        if not telegram_id:
            return None
        if len(str(telegram_id)) < 6:
            raise PydanticCustomError(
                'invalid_telegram_id',
                'must be at least 6 characters long or empty'
            )
        return telegram_id
