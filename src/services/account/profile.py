from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from fastapi.responses import HTMLResponse

from src.utils.templates import source
from src.storage.schemas import UserGet
from src.storage.models import Users


async def verification_gmail(
        request: Request,
        user: Users
) -> Optional[HTMLResponse]:
    if user.is_gmail_verified:
        return None

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