from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse


logout = APIRouter(prefix='/auth/logout', tags=['logout'])


@logout.get('/', response_class=HTMLResponse)
async def get_logout(request: Request,):
    """Disconnects the user from the session"""
    response = RedirectResponse(
        url='/auth/signin',
        status_code=status.HTTP_302_FOUND
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False
    )

    return response
