import smtplib
from email.message import EmailMessage

from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.storage.schemas import UserCreate, UserGet
from src.utils.auth import hash_password, verify_password
from src.utils.data_access_layer import UserDAL
from src.utils.templates import source
from src.utils.validators import validate_model


async def send_verification_email(email_to: str, user_name: str, verification_url: str):
    """Safe async-compatible sending verification link using standard smtplib and Jinja2"""

    template = source.get_template("email_verification.html")
    html_content = template.render(name=user_name, verification_url=verification_url)

    msg = EmailMessage()
    msg["Subject"] = "Verify your Better Price Tracker account"
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = email_to
    msg.set_content(html_content, subtype="html")

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
        print(f"Failed to send email to {email_to}: {e}")


async def authorize_user(
        email: str,
        password: str,
        db_session: AsyncSession,
) -> UserGet:
    data: UserGet = validate_model(
        model_cls=UserGet,
        data={'email': email}
    )

    user = await UserDAL(db_session=db_session).get_user_by(email=email)

    if not user or not verify_password(password, user.hashed_password):
        raise RequestValidationError([
            {
                'type': 'no_field_error',
                'loc': ['body', 'email'],
                'msg': 'Wrong password or email',
                'input': email
            }
        ])

    return UserGet(
        id=user.id,
        name=user.name,
        email=user.email,
        telegram_id=user.telegram_id,
        is_gmail_verified=user.is_gmail_verified,
        is_tg_verified=user.is_tg_verified,
        created_at=user.created_at,
    )


async def register_new_user(
        name: str,
        email: str,
        password: str,
        telegram_id: int | None,
        db_session: AsyncSession,
) -> UserGet:
    """
    Business logic for creating new users.
    :param db_session: Session for database operations
    :param name: Username
    :param email: User email
    :param password: User password (-> hashed password)
    :param telegram_id: Optional user telegram id
    :return:
    """
    data: UserCreate = validate_model(
        model_cls=UserCreate,
        data={'name': name, 'email': email, 'password': password, 'telegram_id': telegram_id},
    )

    user_dal = UserDAL(db_session=db_session)

    if await user_dal.get_user_by(email=email):
        raise RequestValidationError([
            {
                'type': 'no_field_error',
                'loc': ['body', 'email'],
                'msg': 'User with this email already exists',
                'input': email
            }
        ])

    user = await user_dal.create_user(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        telegram_id=data.telegram_id,
    )

    return UserGet(
        id=user.id,
        name=user.name,
        email=user.email,
        telegram_id=user.telegram_id,
        is_gmail_verified=user.is_gmail_verified,
        is_tg_verified=user.is_tg_verified,
        created_at=user.created_at,
    )
