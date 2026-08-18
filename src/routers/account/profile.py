from typing import Optional
import uuid
import zoneinfo

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.account.products import get_user_subscriptions
from src.services.account.profile import verification_gmail
from src.storage.schemas import UserGet
from src.storage.database import get_async_session
from src.utils.auth import get_current_user_by_token
from src.utils.data_access_layer import UserDAL
from src.utils.templates import source


profile = APIRouter(prefix='/profiles', tags=['account'])


@profile.get("/{user_id}", response_class=HTMLResponse)
async def get_user(
        user_id: uuid.UUID,
        request: Request,
        current_user_id: uuid.UUID = Depends(get_current_user_by_token),
        user_timezone: Optional[str] = Cookie(default="UTC"),
        db_session: AsyncSession = Depends(get_async_session),
):
    if current_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    user = await UserDAL(db_session).get_by(id=current_user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await verification_gmail(
        request=request,
        user=user,
    )

    try:
        tz = zoneinfo.ZoneInfo(user_timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    subscriptions = await get_user_subscriptions(user_id=current_user_id, db_session=db_session)
    for sub in subscriptions:
        if sub.product.last_checked_at:
            sub.product.last_checked_at = sub.product.last_checked_at.astimezone(tz)

    user_data = UserGet.model_validate(user)
    user_data.products = subscriptions

    return source.TemplateResponse(
        request=request,
        name='account/profile.html',
        context={
            'title': 'Price Tracker - Profile',
            'user': user_data
        },
    )
