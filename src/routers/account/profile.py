import uuid
import datetime
import decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.account.products import process_product_tracking, remove_product_tracking
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
        db_session: AsyncSession = Depends(get_async_session),
):
    """Get a user by id"""
    if current_user_id != user_id or not (user := await UserDAL(db_session).get_by(id=current_user_id)):
        raise HTTPException(status_code=403, detail="You are not authorized to view this page")

    if not user.is_gmail_verified:
        remaining_seconds = 0

        if user.last_email_sent_at:
            now = datetime.datetime.now(datetime.timezone.utc)
            last_sent = user.last_email_sent_at.replace(
                tzinfo=datetime.timezone.utc) if user.last_email_sent_at.tzinfo is None else user.last_email_sent_at
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
        name='account/account.html',
        context={'title': 'Main Page', 'user': UserGet.model_construct(**user.__dict__)},
    )


@profile.post("/track", response_class=HTMLResponse)
async def track_product(
    request: Request,
    url: str = Form(),
    target_price: decimal.Decimal = Form(),
    current_user_id: uuid.UUID = Depends(get_current_user_by_token),
    db_session: AsyncSession = Depends(get_async_session),
):
    item_context = await process_product_tracking(
        user_id=current_user_id,
        url=url,
        target_price=target_price,
        db_session=db_session
    )

    return source.TemplateResponse(
        request=request,
        name="account/components/product_row.html",
        context={"item": item_context}
    )


@profile.delete("/untrack/{subscription_id}", response_class=Response)
async def untrack_product(
    subscription_id: int,
    current_user_id: uuid.UUID = Depends(get_current_user_by_token),
    db_session: AsyncSession = Depends(get_async_session),
):
    await remove_product_tracking(
        subscription_id=subscription_id,
        user_id=current_user_id,
        db_session=db_session
    )

    return Response(status_code=status.HTTP_200_OK)
