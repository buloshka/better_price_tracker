from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.services.auth import register_new_user, process_verification_email
from src.storage.database import get_async_session
from src.storage.schemas import UserCreate
from src.utils.auth import create_access_token
from src.utils.templates import source
from src.utils.data_access_layer import UserDAL

register = APIRouter(prefix='/auth/signup', tags=['signup'])


@register.get('/', response_class=HTMLResponse)
async def get_signup(request: Request):
    """Sign up page"""
    return source.TemplateResponse(
        request=request,
        name='auth/signup.html',
        context={
            'title': 'Sign Up'
        },
    )


@register.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(..., title='Name'),
    email: EmailStr = Form(..., title='Email'),
    password: str = Form(..., title='Password'),
    telegram_id: Optional[int] = Form(None, title='Telegram ID'),
    db_session: AsyncSession = Depends(get_async_session),
):
    """Create new user"""
    user: UserCreate = await register_new_user(
        name=name,
        email=email,
        password=password,
        telegram_id=telegram_id,
        db_session=db_session,
    )

    access_token = create_access_token(data={"sub": str(user.id)})
    profile_url = request.url_for('get_user', user_id=user.id)

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

    db_user = await UserDAL(db_session=db_session).get_by(id=user.id)
    if db_user:
        await process_verification_email(
            user=db_user,
            db_session=db_session,
            request=request,
            background_tasks=background_tasks,
            force_send=True
        )

    return response
