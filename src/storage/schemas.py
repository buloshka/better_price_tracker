from __future__ import annotations

from typing import Any
from typing import Dict
from typing import cast

from pydantic import ValidationError, field_validator, model_validator
from pydantic_core import ErrorDetails, PydanticCustomError, InitErrorDetails
from pydantic_core import SchemaValidator

import uuid
import datetime
import re

from pydantic import BaseModel, EmailStr, Field, AfterValidator, ConfigDict, StringConstraints, field_validator
from fastapi import Form, HTTPException, status
from typing import Optional, Annotated
from dataclasses import dataclass

from pydantic_core.core_schema import ValidationInfo

ALL_LETTERS = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


def prune(schema: dict) -> None:
    needle: dict | None = schema
    stack = [schema]
    deepest = 0

    while needle:
        if needle := needle.get("schema"):
            stack.append(needle)
            if "fields" in needle:
                deepest = len(stack)

    stack = stack[:deepest]
    if not deepest or len(stack) < 3:
        raise IndexError

    stack[-3]["schema"] = stack[-1]


class ExhaustiveModel(BaseModel):
    def __init__(self, **data: Any) -> None:
        schema = cast(Dict[str, Any], cast(object, self.__pydantic_validator__.__reduce__()[1][0]))
        errors: dict[str, InitErrorDetails] = {}

        try:
            while True:
                try:
                    context = data.pop('__pydantic_context__', None)
                    SchemaValidator(schema).validate_python(data, self_instance=self, context=context)
                    break
                except ValidationError as err:
                    for e in err.errors():
                        error_key = f"{e['loc']}-{e['type']}"

                        errors[error_key] = InitErrorDetails(
                            type=PydanticCustomError(e['type'], e['msg'], e.get('ctx')),
                            loc=e['loc'],
                            input=e.get('input')
                        )

                prune(schema)
        except IndexError:
            pass

        if errors:
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=list(errors.values())
            )

        super().__init__(**data)


class UserGet(ExhaustiveModel):
    id: int = None
    name: str = None
    email: EmailStr
    telegram_id: Optional[int] = None
    created_at: datetime.datetime = None

    @model_validator(mode='before')
    @classmethod
    def validate_credentials(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        context = info.context
        if not context or 'db' not in context:
            return data

        db = context['db']
        password_to_check = context.get("password")
        user_found = False

        for uid, udata in db.items():
            if udata.get("email") == data.get("email"):
                if udata.get("password") == password_to_check:
                    user_found = True
                    data["id"] = uid
                    data["name"] = udata.get("name")
                    data["telegram_id"] = udata.get("telegram_id")
                    data["created_at"] = udata.get("created_at")
                    break

        if not user_found:
            raise PydanticCustomError('no_field_error', 'Wrong password or email')

        return data


class UserCreate(ExhaustiveModel):  # Ваша базовая ExhaustiveModel
    name: Annotated[str, Field(min_length=2, max_length=255)]
    email: Annotated[EmailStr, Field(min_length=5)]
    password: Annotated[str, Field(min_length=6, max_length=64)]
    telegram_id: Annotated[Optional[int], Field(default=None)]
    created_at: Annotated[datetime.datetime, Field(default_factory=datetime.datetime.now)]
    telegram_code: Annotated[Optional[int], Field(default=None)]

    @field_validator('name', mode='after')
    @classmethod
    def name_validator(cls, name: str) -> str:
        if re.match(ALL_LETTERS, name.strip()) is None:
            raise ValueError('must contain only letters')
        return name

    @field_validator('email', mode='after')
    @classmethod
    def email_unique_validator(cls, email: EmailStr, info: ValidationInfo) -> EmailStr:
        context = info.context
        if not context or 'db' not in context:
            return email

        db = context['db']
        for udata in db.values():
            if udata.get("email") == email:
                raise ValueError('already registered')

        return email

    @field_validator('telegram_id', mode='after')
    @classmethod
    def telegram_id_validator(cls, telegram_id: int) -> Optional[int]:
        if not telegram_id:
            return None
        if len(str(telegram_id)) < 6:
            raise ValueError('must be at least 6 characters long')
