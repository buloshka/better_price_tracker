from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.schemas import UserCreate, UserGet
from src.utils.data_access_layer import ProductDAL

