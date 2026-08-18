import datetime
import decimal
import uuid

from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models import UsersProducts, Products
from src.storage.schemas import UserProductCreate, UserProductGet, ProductGet
from src.utils.data_access_layer import ProductDAL, UsersProductsDAL
from src.scrapers.factory import ScraperFactory
from src.utils.images import download_product_image
from src.utils.validators import validate_model


async def get_user_subscriptions(
        user_id: uuid.UUID,
        db_session: AsyncSession,
        limit: int = 20,
        offset: int = 0,
) -> list[UserProductGet]:
    stmt = (
        select(UsersProducts)
        .where(UsersProducts.user_id == user_id)
        .options(
            joinedload(UsersProducts.product).selectinload(Products.price_history)
        )
        .order_by(UsersProducts.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db_session.execute(stmt)
    subscriptions = result.scalars().all()

    return [UserProductGet.model_validate(sub) for sub in subscriptions]


async def process_product_tracking(
        user_id: uuid.UUID,
        url: str,
        target_price: decimal.Decimal,
        db_session: AsyncSession,
) -> UserProductGet:
    """
    Logic for adding a new product to tracking.
    """
    data: UserProductCreate = validate_model(
        model_cls=UserProductCreate,
        data={'url': url, 'target_price': target_price},
    )

    product_dal = ProductDAL(db_session=db_session)
    ups_dal = UsersProductsDAL(db_session=db_session)

    product = await product_dal.get_by(url=data.url)

    if not product:
        try:
            pipeline = ScraperFactory.create(data.url)
            async with pipeline:
                scraped_data = await pipeline.run()

            local_image_path = await download_product_image(scraped_data.photo)

            product = await product_dal.create(
                url=data.url,
                title=scraped_data.title,
                description=scraped_data.description,
                image_url=local_image_path,
                current_price=scraped_data.price,
                last_checked_at=datetime.datetime.now(datetime.timezone.utc)
            )
        except Exception as exc:
            raise RequestValidationError([
                {
                    'type': 'no_field_error',
                    'loc': ['body', 'url'],
                    'msg': f"Scraper failure: {str(exc)}",
                    'input': url
                }
            ])

    if product.current_price and data.target_price >= product.current_price:
        raise RequestValidationError([
            {
                'type': 'no_field_error',
                'loc': ['body', 'target_price'],
                'msg': f"Target price must be strictly lower than the current price ({product.current_price} ₽)",
                'input': str(data.target_price)
            }
        ])

    existing_link = await ups_dal.get_by(user_id=user_id, product_id=product.id)
    if existing_link:
        raise RequestValidationError([
            {
                'type': 'no_field_error',
                'loc': ['body', 'url'],
                'msg': "You are already tracking this product link",
                'input': url
            }
        ])

    subscription = await ups_dal.create(
        user_id=user_id,
        product_id=product.id,
        target_price=data.target_price
    )

    stmt = (
        select(UsersProducts)
        .where(UsersProducts.id == subscription.id)
        .options(
            joinedload(UsersProducts.product).selectinload(Products.price_history)
        )
    )
    result = await db_session.execute(stmt)
    db_subscription = result.scalar_one()

    return UserProductGet.model_validate(db_subscription)


async def remove_product_tracking(
        subscription_id: int,
        user_id: uuid.UUID,
        db_session: AsyncSession,
) -> bool:
    """
    Logic for deleting a subscription.
    """
    ups_dal = UsersProductsDAL(db_session=db_session)

    subscription = await ups_dal.get_by(id=subscription_id)
    if not subscription or subscription.user_id != user_id:
        raise RequestValidationError([
            {
                'type': 'no_field_error',
                'loc': ['body', 'id'],
                'msg': "Tracker subscription not found or access denied",
                'input': subscription_id
            }
        ])

    return await ups_dal.delete_by(id=subscription_id)
