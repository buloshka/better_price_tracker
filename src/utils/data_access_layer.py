import uuid
from typing import Optional, overload, Any

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

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
        await self.db_session.commit()

        return new_user

    # --- СЕКЦИЯ ПОЛУЧЕНИЯ ПОЛЬЗОВАТЕЛЯ (GET) ---
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

    async def update_user(self, user_id: uuid.UUID, **kwargs: Any) -> Optional[Users]:
        """
        Dynamically updates specific user fields by user_id.
        Example: await dal.update_user(user_id, is_gmail_verified=True)
        """
        if not kwargs:
            return await self.get_user_by(id=user_id)

        query = (
            update(Users)
            .where(Users.id == user_id)
            .values(**kwargs)
        )
        await self.db_session.execute(query)
        await self.db_session.commit()

        return await self.get_user_by(id=user_id)

    @overload
    async def delete_user_by(self, *, id: uuid.UUID) -> bool:
        ...

    @overload
    async def delete_user_by(self, *, email: str) -> bool:
        ...

    async def delete_user_by(
            self,
            *,
            id: Optional[uuid.UUID] = None,
            email: Optional[str] = None,
    ) -> bool:
        """
        Deletes a user by id or email using RETURNING clause.
        """
        query = delete(Users).returning(Users.id)

        if id is not None:
            query = query.where(Users.id == id)
        elif email is not None:
            query = query.where(Users.email == email)
        else:
            return False

        result = await self.db_session.execute(query)
        await self.db_session.commit()

        deleted_id = result.scalar_one_or_none()

        return deleted_id is not None
