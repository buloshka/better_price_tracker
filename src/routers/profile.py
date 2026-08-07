import uuid

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from src.utils.templates import source
from src.storage.models import users_db
from src.utils.auth import get_current_user_by_token


profile = APIRouter(prefix='/profiles', tags=['profile'])


@profile.get("/{user_id}", response_class=HTMLResponse)
async def get_user(
    user_id: uuid.UUID,
    request: Request,
    current_user_id: int = Depends(get_current_user_by_token)
):
    """Get a user by id"""
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this page"
        )

    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    return source.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'title': 'Main Page',
            'user': users_db[user_id]
        },
    )
