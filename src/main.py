from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from src.utils.templates import source


app = FastAPI(
    title='Price Tracker',
)

@app.get(path='/', response_class=HTMLResponse)
async def read_root(request: Request):
    return source.TemplateResponse(
        request=request,
        name='index.html',
        context={'my_custom_id': 2}
    )
