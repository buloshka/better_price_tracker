import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, overload

from src.storage.models import Users


class UserDAL:
    """Data access layer for operating users info"""
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_user(self, name: str, email: str, hashed_password: str, telegram_id: Optional[int] = None) -> Users:
        new_user = Users(
            name=name,
            email=email,
            hashed_password=hashed_password,
            telegram_id=telegram_id,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()

        return new_user

    @overload
    async def get_user_by(self, *, id: uuid.UUID) -> Optional[Users]:
        ...

    @overload
    async def get_user_by(self, *, email: str) -> Optional[Users]:
        ...

    async def get_user_by(
            self,
            *,
            id: Optional[uuid.UUID] = None,
            email: Optional[str] = None,
    ) -> Optional[Users]:
        query = select(Users)

        if id is not None:
            query = query.where(Users.id == id)
        elif email is not None:
            query = query.where(Users.email == email)
        else:
            return None

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
