from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.services.auth import authorize_user
from src.storage.database import get_async_session
from src.storage.schemas import UserGet
from src.utils.auth import create_access_token
from src.utils.templates import source

login = APIRouter(prefix='/auth/signin', tags=['signin'])


@login.get('/', response_class=HTMLResponse)
async def get_signin(request: Request):
    """Login page"""
    return source.TemplateResponse(
        request=request,
        name='auth/signin.html',
        context={
            'title': 'Sign In'
        }
    )


@login.post("/", status_code=status.HTTP_200_OK)
async def login_user(
    request: Request,
    email: EmailStr = Form(..., title='Email'),
    password: str = Form(..., title='Password'),
    db_session: AsyncSession = Depends(get_async_session),
):
    """Authenticate user with smart email resend protection"""
    user: UserGet = await authorize_user(
        email=email,
        password=password,
        db_session=db_session,
    )

    access_token = create_access_token(data={"sub": str(user.id)})
    profile_url = request.url_for('get_user', user_id=user.id)

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
