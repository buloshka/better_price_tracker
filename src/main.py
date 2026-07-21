from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from src.utils.templates import source
from src.routers.login import router as login


app = FastAPI(
    title='Price Tracker',
)

@app.get(path='/', response_class=HTMLResponse)
async def read_root(request: Request):
    """Redirect to login page"""
    return source.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'title': 'Main Page',
        }
    )


app.include_router(login)
