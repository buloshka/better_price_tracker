import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.schemas import UserGet
from src.storage.database import get_async_session
from src.utils.auth import get_current_user_by_token
from src.utils.data_access_layer import UserDAL
from src.utils.templates import source

profile = APIRouter(prefix='/profiles', tags=['profile'])


@profile.get("/{user_id}", response_class=HTMLResponse)
async def get_user(
        user_id: uuid.UUID,
        request: Request,
        current_user_id: uuid.UUID = Depends(get_current_user_by_token),
        db_session: AsyncSession = Depends(get_async_session),
):
    """Get a user by id"""
    if current_user_id != user_id or not (user := await UserDAL(db_session).get_user_by(id=current_user_id)):
        raise HTTPException(status_code=403, detail="You are not authorized to view this page")

    if not user.is_gmail_verified:
        remaining_seconds = 0

        if user.last_email_sent_at:
            now = datetime.now(timezone.utc)
            last_sent = user.last_email_sent_at.replace(
                tzinfo=timezone.utc) if user.last_email_sent_at.tzinfo is None else user.last_email_sent_at
            elapsed = (now - last_sent).total_seconds()

            if elapsed < 120:
                remaining_seconds = int(120 - elapsed)

        return source.TemplateResponse(
            request=request,
            name='email/status.html',
            context={
                'title': 'Verify Your Email',
                'user': UserGet.model_construct(**user.__dict__),
                'remaining_seconds': remaining_seconds,
            },
        )

    return source.TemplateResponse(
        request=request,
        name='account/profile.html',
        context={'title': 'Main Page', 'user': UserGet.model_construct(**user.__dict__)},
    )
