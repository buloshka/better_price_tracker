import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from fastapi import Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.storage.models import Users
from src.utils.auth import create_verification_token
from src.utils.data_access_layer import UserDAL
from src.utils.templates import source


async def send_verification_email(email_to: str, user_name: str, verification_url: str):
    """Safe async-compatible sending verification link using standard smtplib and Jinja2"""

    template = source.get_template('email/letter_template.html')
    html_content = template.render(name=user_name, verification_url=verification_url)

    msg = EmailMessage()
    msg['Subject'] = 'Verify your Better Price Tracker account'
    msg['From'] = f'{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>'
    msg['To'] = email_to
    msg.set_content(html_content, subtype='html')

    try:
        if settings.MAIL_PORT == 465:
            with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
                server.starttls()
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                server.send_message(msg)
    except Exception as e:
        print(f'Failed to send email to {email_to}: {e}')


async def process_verification_email(
        user: Users,
        db_session: AsyncSession,
        request: Request,
        background_tasks: BackgroundTasks,
        force_send: bool = False
) -> int:
    """
    Business logic for checking verification email timeout and managing background send tasks.
    Returns remaining_seconds if locked, or 0 if email was successfully dispatched.
    """
    now = datetime.now(timezone.utc)

    if user.last_email_sent_at and not force_send:
        last_sent = user.last_email_sent_at.replace(
            tzinfo=timezone.utc) if user.last_email_sent_at.tzinfo is None else user.last_email_sent_at
        elapsed = (now - last_sent).total_seconds()
        if elapsed < 120:
            return int(120 - elapsed)

    user_dal = UserDAL(db_session=db_session)
    await user_dal.update(user_id=user.id, last_email_sent_at=now)

    verify_token = create_verification_token(data={'sub': str(user.id)})
    email_link = str(request.url_for('verify_email', token=verify_token))

    background_tasks.add_task(
        send_verification_email,
        email_to=user.email,
        user_name=user.name,
        verification_url=email_link
    )

    return 0
