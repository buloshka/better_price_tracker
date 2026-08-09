from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.schemas import UserCreate, UserGet
from src.utils.auth import hash_password, verify_password
from src.utils.data_access_layer import UserDAL
from src.utils.validators import validate_model


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
        created_at=user.created_at
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
        created_at=user.created_at,
    )
