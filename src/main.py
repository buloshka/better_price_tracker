from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory='src/templates')

app = FastAPI(
    title='Price Tracker',
)

@app.get(path='/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'my_custom_id': 2}
    )
