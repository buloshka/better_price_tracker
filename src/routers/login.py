from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from src.utils.templates import source


router = APIRouter(prefix='/auth/signin', tags=['auth'])

@router.get(path='/', response_class=HTMLResponse)
async def signin(request: Request):
    """Main login page"""
    return source.TemplateResponse(
        request=request,
        name='signin.html',
        context={
            'title': 'Sign In',
        },
    )
