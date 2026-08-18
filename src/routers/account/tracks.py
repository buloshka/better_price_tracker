import uuid
import zoneinfo
import decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, Response, status, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.account.products import process_product_tracking, remove_product_tracking, get_user_subscriptions
from src.storage.database import get_async_session
from src.utils.auth import get_current_user_by_token
from src.utils.templates import source


tracks = APIRouter(prefix='/tracks', tags=['account'])


@tracks.post("/create", response_class=HTMLResponse)
async def track_product(
    request: Request,
    url: str = Form(),
    target_price: decimal.Decimal = Form(),
    current_user_id: uuid.UUID = Depends(get_current_user_by_token),
    user_timezone: Optional[str] = Cookie(default="UTC"),
    db_session: AsyncSession = Depends(get_async_session),
):
    new_item = await process_product_tracking(
        user_id=current_user_id,
        url=url,
        target_price=target_price,
        db_session=db_session
    )

    try:
        tz = zoneinfo.ZoneInfo(user_timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    new_item.created_at = new_item.created_at.astimezone(tz)

    return source.TemplateResponse(
        request=request,
        name="account/components/product_row.html",
        context={"item": new_item}
    )


@tracks.delete("/delete/{subscription_id}", response_class=Response)
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


@tracks.get("/load-more", response_class=HTMLResponse)
async def load_more_products(
        request: Request,
        offset: int = 0,
        current_user_id: uuid.UUID = Depends(get_current_user_by_token),
        user_timezone: Optional[str] = Cookie(default="UTC"),
        db_session: AsyncSession = Depends(get_async_session),
):
    subscriptions = await get_user_subscriptions(
        user_id=current_user_id,
        db_session=db_session,
        offset=offset
    )

    if not subscriptions:
        return HTMLResponse(content="")

    try:
        tz = zoneinfo.ZoneInfo(user_timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    html_content = ""
    for item in subscriptions:
        item.created_at = item.created_at.astimezone(tz)
        html_content += source.templates.get_template("account/components/product_row.html").render(
            {"item": item, "request": request}
        )

    return HTMLResponse(content=html_content)
