from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.routers.auth import login, register


app = FastAPI(
    title='Price Tracker',
)

app.mount('/static', StaticFiles(directory='src/static'), name='static')


@app.get(path='/', response_class=HTMLResponse)
async def get_root(request: Request):
    """Auto-redirect to login page"""
    login_url = request.url_for('get_signin')

    return RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)


app.include_router(login)
app.include_router(register)
