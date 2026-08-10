import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from jose import jwt, JWTError

from src.config import settings
from src.services.auth import authorize_user, register_new_user, send_verification_email
from src.storage.database import get_async_session
from src.storage.schemas import UserCreate, UserGet
from src.utils.auth import create_access_token, create_verification_token
from src.utils.templates import source
from src.utils.data_access_layer import UserDAL


login = APIRouter(prefix='/auth/signin', tags=['auth'])
register = APIRouter(prefix='/auth/signup', tags=['auth'])


@login.get(path='/', response_class=HTMLResponse)
async def get_signin(request: Request):
    """Login page"""
    return source.TemplateResponse(
        request=request,
        name='signin.html',
        context={
            'title': 'Sign In',
        }
    )


@login.post("/", status_code=status.HTTP_200_OK)
async def login_user(
        request: Request,
        background_tasks: BackgroundTasks,
        email: EmailStr = Form(..., title='Email'),
        password: str = Form(..., title='Password'),
        db_session: AsyncSession = Depends(get_async_session),
):
    """Authenticate user"""
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

    if not user.is_gmail_verified:
        verify_token = create_verification_token(data={"sub": str(user.id)})
        email_link = request.url_for('verify_email', token=verify_token)
        background_tasks.add_task(
            send_verification_email,
            email_to=user.email,
            user_name=user.name,
            verification_url=str(email_link)
        )

    return response


@register.get(path='/', response_class=HTMLResponse)
async def get_signup(request: Request):
    """Sign up page"""
    return source.TemplateResponse(
        request=request,
        name='signup.html',
        context={
            'title': 'Sign Up',
        }
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

    verify_token = create_verification_token(data={"sub": str(user.id)})
    email_link = request.url_for('verify_email', token=verify_token)
    background_tasks.add_task(
        send_verification_email,
        email_to=user.email,
        user_name=user.name,
        verification_url=str(email_link),
    )

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


@login.get(path='/verify-email/{token}', response_class=RedirectResponse)
async def verify_email(
        token: str,
        request: Request,
        db_session: AsyncSession = Depends(get_async_session)
):
    """Gmail verification with token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=400,
                detail="Invalid verification token"
            )
        user_uuid = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Verification link has expired or is invalid"
        )

    user_dal = UserDAL(db_session=db_session)
    user = await user_dal.get_user_by(id=user_uuid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.is_gmail_verified:
        user.is_gmail_verified = True
        await db_session.commit()

    profile_url = request.url_for('get_user', user_id=user.id)
    return RedirectResponse(
        url=str(profile_url),
        status_code=status.HTTP_302_FOUND
    )
