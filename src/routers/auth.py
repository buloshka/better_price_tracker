from fastapi.exceptions import RequestValidationError
from pydantic import EmailStr, ValidationError
from fastapi import APIRouter, Request, status, Response, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional, Union

from src.utils.templates import source
from src.utils.auth import create_access_token
from src.storage.schemas import UserCreate, UserGet
from src.storage.models import users_db


login = APIRouter(prefix='/auth/signin', tags=['auth'])
register = APIRouter(prefix='/auth/signup', tags=['auth'])


@login.get(path='/', response_class=HTMLResponse)
async def get_signin(request: Request):
    """Login page"""
    return source.TemplateResponse(
        request=request, name='signin.html', context={'title': 'Sign In'}
    )


@login.post("/", status_code=status.HTTP_200_OK)
async def login_user(
        request: Request,
        email: EmailStr = Form(...),
        password: str = Form(...)
):
    """Authenticate user"""
    try:
        data = UserGet(
            email=email,
            __pydantic_context__={
                "db": users_db,
                "password": password,
            }
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors())

    user_id = data.id

    access_token = create_access_token(data={"sub": str(user_id)})

    profile_url = request.url_for('get_user', user_id=user_id)
    response = HTMLResponse(status_code=status.HTTP_200_OK)
    response.headers["HX-Redirect"] = str(profile_url)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600
    )

    return response


@register.get(path='/', response_class=HTMLResponse)
async def get_signup(request: Request):
    """Sign up page"""
    return source.TemplateResponse(
        request=request, name='signup.html', context={'title': 'Sign Up'}
    )


@register.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        telegram_id: Optional[int] = Form(default=None),
):
    """Create new user"""
    try:
        data = UserCreate(
            name=name,
            email=email,
            password=password,
            telegram_id=telegram_id,
            __pydantic_context__={"db": users_db}
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors())

    user_id = max(users_db.keys()) + 1 if users_db else 1

    users_db[user_id] = data.model_dump()
    users_db[user_id]["created_at"] = "2026-08-04"

    access_token = create_access_token(data={"sub": str(user_id)})

    profile_url = request.url_for('get_user', user_id=user_id)
    response = HTMLResponse(status_code=status.HTTP_201_CREATED)
    response.headers["HX-Redirect"] = str(profile_url)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600
    )

    return response
