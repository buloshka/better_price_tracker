from typing import Optional
import uuid
import zoneinfo

from fastapi import APIRouter, Depends, Form, status, Request, Cookie, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.config import settings
from src.services.account.telegram import process_verification_tg
from src.services.auth import process_verification_email
from src.storage.schemas import UserGet
from src.storage.database import get_async_session
from src.utils.auth import get_current_user_by_token
from src.utils.data_access_layer import UserDAL
from src.utils.templates import source


settings_router = APIRouter(prefix='/profiles/settings', tags=['settings'])


@settings_router.get("/", response_class=HTMLResponse)
async def get_settings(
        request: Request,
        current_user_id: uuid.UUID = Depends(get_current_user_by_token),
        user_timezone: Optional[str] = Cookie(default="UTC"),
        db_session: AsyncSession = Depends(get_async_session),
):
    user = await UserDAL(db_session).get_by(id=current_user_id)
    user_data = UserGet(
        id=user.id,
        name=user.name,
        email=user.email,
        is_gmail_verified=user.is_gmail_verified,
        telegram_id=user.telegram_id,
        is_tg_verified=user.is_tg_verified,
        created_at=user.created_at,
    )

    try:
        tz = zoneinfo.ZoneInfo(user_timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    user_data.created_at = user_data.created_at.astimezone(tz)

    return source.TemplateResponse(
        request=request,
        name='account/settings.html',
        context={
            'title': 'Profile Settings',
            'user': user_data
        },
    )


@settings_router.post("/change-email", response_class=HTMLResponse)
async def change_email(
        request: Request,
        background_tasks: BackgroundTasks,
        new_email: EmailStr = Form(...),
        current_user_id: uuid.UUID = Depends(get_current_user_by_token),
        db_session: AsyncSession = Depends(get_async_session),
):
    user = await UserDAL(db_session).update(
        user_id=current_user_id,
        is_gmail_verified=False,
        email=new_email,
    )

    await process_verification_email(
        user=user,
        db_session=db_session,
        request=request,
        background_tasks=background_tasks,
        force_send=True
    )

    profile_url = request.url_for('get_user', user_id=user.id)
    response = HTMLResponse(status_code=status.HTTP_200_OK)
    response.headers["HX-Redirect"] = str(profile_url)

    return response


@settings_router.post("/change-tg", response_class=HTMLResponse)
async def change_telegram(
        request: Request,
        background_tasks: BackgroundTasks,
        new_tg_id: int = Form(...),
        current_user_id: uuid.UUID = Depends(get_current_user_by_token),
        db_session: AsyncSession = Depends(get_async_session),
):
    user = await UserDAL(db_session).update(
        user_id=current_user_id,
        is_tg_verified = False,
        telegram_id=new_tg_id,
    )

    await process_verification_tg(
        user=user,
        request=request,
        background_tasks=background_tasks,
    )

    return HTMLResponse(
        content="<span class='text-verification-warning'>Verification pending. Please confirm via your Telegram bot.</span>"
    )


@settings_router.get('/verify-tg/{token}', response_class=RedirectResponse)
async def verify_tg(
    token: str,
    request: Request,
    db_session: AsyncSession = Depends(get_async_session)
):
    """Telegram verification with token"""
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
    user = await user_dal.get_by(id=user_uuid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.is_tg_verified:
        await user_dal.update(user_id=user.id, is_tg_verified=True)

    settings_url = request.url_for('get_settings')
    return RedirectResponse(
        url=str(settings_url),
        status_code=status.HTTP_302_FOUND
    )
