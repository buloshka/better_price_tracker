from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from src.utils.templates import source


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
            'title': 'Sign Un',
        },
    )
