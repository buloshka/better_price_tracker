from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.storage.database import get_async_session
from src.storage.schemas import UserAuthData
from src.storage.models import Users


class UserDAL:
    """Data access layer for operating users info"""
    def __init__(self, db_session: AsyncSession = Depends(get_async_session)) -> None:
        self.db_session = db_session

    async def create_user(self, data: UserAuthData):
        user = Users(data=data)
        self.db_session.add(user)
        await self.db_session.flush()

        return user
