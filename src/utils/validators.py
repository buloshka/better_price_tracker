import uuid

from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

from src.config import settings

from typing import Type, Any, Dict, Optional, NoReturn, Union
from pydantic import BaseModel, ValidationError
from fastapi.exceptions import RequestValidationError


def validate_model(
    model_cls: Type[BaseModel],
    data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Union[Type[BaseModel], NoReturn]:
    """
    Validator for any pydantic models.
    Auto-catching ValidationError exceptions and turn into RequestValidationError for HTMX.
    :param model_cls: Pydantic model
    :param data: Data to be validated
    :param context: Optional context for validation
    :return:
    """
    try:
        return model_cls.model_validate(data, context=context)
    except ValidationError as exc:
        error_to_raise = RequestValidationError(exc.errors())
        error_to_raise.model_name = model_cls.__name__
        raise error_to_raise
