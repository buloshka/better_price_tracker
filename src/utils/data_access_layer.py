import abc
import uuid
from typing import Optional, overload, Any

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models import Base, Users, Products, UsersProducts


class BaseDAL(abc.ABC):
    """Data access layer for operating database items"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    @abc.abstractmethod
    async def create(self, **kwargs: Any) -> Base:
        """
        Create method.
        Must be implemented by subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by(self, **kwargs: Any) -> Optional[Base]:
        """
        Get some data from DB by something.
        Must be implemented by subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, **kwargs: Any) -> Optional[Base]:
        """
        Update method.
        Must be implemented by subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_by(self, **kwargs: Any) -> bool:
        """
        Delete some data from DB by something.
        Must be implemented by subclass.
        """
        raise NotImplementedError


class UserDAL(BaseDAL):
    """Data access layer for operating users info"""

    async def create(self, **kwargs: Any) -> Users:
        """
        Creates a new user in the database.
        Expected kwargs: name, email, hashed_password, telegram_id (optional)
        """
        new_user = Users(**kwargs)
        self.db_session.add(new_user)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_user

    @overload
    async def get_by(self, *, id: uuid.UUID) -> Optional[Users]:
        ...

    @overload
    async def get_by(self, *, email: str) -> Optional[Users]:
        ...

    async def get_by(
            self,
            *,
            id: Optional[uuid.UUID] = None,
            email: Optional[str] = None,
    ) -> Optional[Users]:
        """Gets a user filter by id or email address."""
        query = select(Users)

        if id is not None:
            query = query.where(Users.id == id)
        elif email is not None:
            query = query.where(Users.email == email)
        else:
            return None

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, *, user_id: uuid.UUID, **kwargs: Any) -> Optional[Users]:
        """
        Dynamically updates specific user fields by user_id.
        Example: await user_dal.update(user_id=uid, is_gmail_verified=True)
        """
        if not kwargs:
            return await self.get_by(id=user_id)

        query = (
            update(Users)
            .where(Users.id == user_id)
            .values(**kwargs)
        )
        await self.db_session.execute(query)
        await self.db_session.commit()

        return await self.get_by(id=user_id)

    @overload
    async def delete_by(self, *, id: uuid.UUID) -> bool:
        ...

    @overload
    async def delete_by(self, *, email: str) -> bool:
        ...

    async def delete_by(
            self,
            *,
            id: Optional[uuid.UUID] = None,
            email: Optional[str] = None,
    ) -> bool:
        """Deletes a user by id or email using RETURNING clause."""
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


class ProductDAL(BaseDAL):
    """Data access layer for operating products info"""

    async def create(self, **kwargs: Any) -> Products:
        """
        Creates a new product in the database.
        Expected kwargs: url, title, description (optional), image_url (optional), current_price (optional)
        """
        new_product = Products(**kwargs)
        self.db_session.add(new_product)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_product

    @overload
    async def get_by(self, *, id: int) -> Optional[Products]:
        ...

    @overload
    async def get_by(self, *, url: str) -> Optional[Products]:
        ...

    async def get_by(
        self,
        *,
        id: Optional[int] = None,
        url: Optional[str] = None,
    ) -> Optional[Products]:
        """Gets a product filtered by database id or unique clean url."""
        query = select(Products)

        if id is not None:
            query = query.where(Products.id == id)
        elif url is not None:
            query = query.where(Products.url == url)
        else:
            return None

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, *, product_id: int, **kwargs: Any) -> Optional[Products]:
        """
        Dynamically updates global product fields (e.g., current_price, last_checked_at).
        Example: await product_dal.update(product_id=1, current_price=5300, last_checked_at=func.current_timestamp())
        """
        if not kwargs:
            return await self.get_by(id=product_id)

        query = (
            update(Products)
            .where(Products.id == product_id)
            .values(**kwargs)
        )
        await self.db_session.execute(query)
        await self.db_session.commit()

        return await self.get_by(id=product_id)

    @overload
    async def delete_by(self, *, id: int) -> bool:
        ...

    @overload
    async def delete_by(self, *, url: str) -> bool:
        ...

    async def delete_by(
        self,
        *,
        id: Optional[int] = None,
        url: Optional[str] = None,
    ) -> bool:
        """Deletes a product by id or url using RETURNING clause."""
        query = delete(Products).returning(Products.id)

        if id is not None:
            query = query.where(Products.id == id)
        elif url is not None:
            query = query.where(Products.url == url)
        else:
            return False

        result = await self.db_session.execute(query)
        await self.db_session.commit()

        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None


class UsersProductsDAL(BaseDAL):
    """Data access layer for operating user product subscriptions (junction table)"""

    async def create(self, **kwargs: Any) -> UsersProducts:
        """
        Creates a new user-product tracking subscription.
        Expected kwargs: user_id, product_id, target_price, is_notification_enabled (optional)
        """
        new_subscription = UsersProducts(**kwargs)
        self.db_session.add(new_subscription)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_subscription

    # --- GET SECTION WITH OVERLOADS ---
    @overload
    async def get_by(self, *, id: int) -> Optional[UsersProducts]:
        ...

    @overload
    async def get_by(self, *, user_id: uuid.UUID, product_id: int) -> Optional[UsersProducts]:
        ...

    async def get_by(
        self,
        *,
        id: Optional[int] = None,
        user_id: Optional[uuid.UUID] = None,
        product_id: Optional[int] = None,
    ) -> Optional[UsersProducts]:
        """Gets a subscription filtered by its specific id or unique user_id + product_id pair."""
        query = select(UsersProducts)

        if id is not None:
            query = query.where(UsersProducts.id == id)
        elif user_id is not None and product_id is not None:
            query = query.where(
                UsersProducts.user_id == user_id,
                UsersProducts.product_id == product_id
            )
        else:
            return None

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    # --- UPDATE SECTION ---
    async def update(self, *, subscription_id: int, **kwargs: Any) -> Optional[UsersProducts]:
        """
        Dynamically updates specific user subscription fields (e.g., target_price, is_notification_enabled).
        Example: await ups_dal.update(subscription_id=1, target_price=4999.00)
        """
        if not kwargs:
            return await self.get_by(id=subscription_id)

        query = (
            update(UsersProducts)
            .where(UsersProducts.id == subscription_id)
            .values(**kwargs)
        )
        await self.db_session.execute(query)
        await self.db_session.commit()

        return await self.get_by(id=subscription_id)

    # --- DELETE SECTION WITH OVERLOADS ---
    @overload
    async def delete_by(self, *, id: int) -> bool:
        ...

    @overload
    async def delete_by(self, *, user_id: uuid.UUID, product_id: int) -> bool:
        ...

    async def delete_by(
        self,
        *,
        id: Optional[int] = None,
        user_id: Optional[uuid.UUID] = None,
        product_id: Optional[int] = None,
    ) -> bool:
        """Deletes a tracking subscription using returning clause by id or user_id + product_id combination."""
        query = delete(UsersProducts).returning(UsersProducts.id)

        if id is not None:
            query = query.where(UsersProducts.id == id)
        elif user_id is not None and product_id is not None:
            query = query.where(
                UsersProducts.user_id == user_id,
                UsersProducts.product_id == product_id
            )
        else:
            return False

        result = await self.db_session.execute(query)
        await self.db_session.commit()

        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None
