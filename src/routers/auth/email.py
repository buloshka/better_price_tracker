import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from src.config import settings
from src.services.auth import process_verification_email
from src.storage.database import get_async_session
from src.utils.auth import get_current_user_by_token
from src.utils.templates import source
from src.utils.data_access_layer import UserDAL

email = APIRouter(prefix='/auth/email', tags=['email'])


@email.get('/verify-email/{token}', response_class=RedirectResponse)
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
    user = await user_dal.get_by(id=user_uuid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.is_gmail_verified:
        await user_dal.update(user_id=user.id, is_gmail_verified=True)

    profile_url = request.url_for('get_user', user_id=user.id)
    return RedirectResponse(
        url=str(profile_url),
        status_code=status.HTTP_302_FOUND
    )


@email.post("/resend-verification", response_class=HTMLResponse)
async def resend_verification(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user_id: uuid.UUID = Depends(get_current_user_by_token),
    db_session: AsyncSession = Depends(get_async_session)
):
    """Resend verification email with a hard server-side 2-minute check"""
    user_dal = UserDAL(db_session=db_session)
    user = await user_dal.get_by(id=current_user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_gmail_verified:
        return HTMLResponse(
            content="Email is already verified!",
            status_code=200
        )

    remaining_seconds = await process_verification_email(
        user=user, db_session=db_session, request=request, background_tasks=background_tasks
    )

    if remaining_seconds > 0:
        return source.TemplateResponse(
            request=request,
            name='email/components/button_countdown.html',
            context={
                'remaining_seconds': remaining_seconds,
                'time_string': '00:00'
            }
        )

    response = source.TemplateResponse(
        request=request,
        name='email/components/button_countdown.html',
        context={
            'remaining_seconds': 120,
            'time_string': '02:00'
        }
    )
    response.headers["HX-Trigger"] = "emailSentSuccess"
    return response


@email.get("/resend-button-active", response_class=HTMLResponse)
async def get_active_resend_button(request: Request):
    """Return active resend button из HTML-шаблона"""
    return source.TemplateResponse(
        request=request,
        name='email/components/button_active.html'
    )
