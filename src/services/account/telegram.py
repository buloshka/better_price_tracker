from fastapi import Request, BackgroundTasks

from src.tg_bot import send_verification_tg
from src.storage.models import Users
from src.utils.auth import create_verification_token


async def process_verification_tg(
        user: Users,
        request: Request,
        background_tasks: BackgroundTasks
):
    """
    Business logic for checking verification tg timeout and managing background send tasks.
    """
    verify_token = create_verification_token(data={'sub': str(user.id)})
    tg_link = str(request.url_for('verify_tg', token=verify_token))

    background_tasks.add_task(
        send_verification_tg,
        tg_to=user.telegram_id,
        user_name=user.name,
        verification_url=tg_link
    )

    return 0
