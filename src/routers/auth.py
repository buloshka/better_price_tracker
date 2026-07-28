import secrets

from fastapi import APIRouter, Request, status
from fastapi import HTTPException
from fastapi.responses import HTMLResponse

from src.utils.templates import source
from src.storage.schemas import UserResponse

from src.main import users_db


login = APIRouter(prefix='/auth/signin', tags=['auth'])
register = APIRouter(prefix='/auth/signup', tags=['auth'])


@login.get(path='/', response_class=HTMLResponse)
async def get_signin(request: Request):
    """Main login page"""
    return source.TemplateResponse(
        request=request,
        name='signin.html',
        context={
            'title': 'Sign In',
        },
    )


@register.get(path='/', response_class=HTMLResponse)
async def get_signup(request: Request):
    """Main signup page"""
    return source.TemplateResponse(
        request=request,
        name='signup.html',
        context={
            'title': 'Sign Up',
        },
    )


@register.post("/users/{user_id}/telegram-link", response_model=UserResponse)
def generate_telegram_link(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    token = secrets.token_urlsafe(16)
    users_db[user_id]["telegram_token"] = token

    return users_db[user_id]
