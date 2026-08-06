import re

from fastapi import FastAPI, Request, status, HTTPException

from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from src.routers.auth import login, register
from src.routers.profile import profile

app = FastAPI(title='Price Tracker')

app.mount('/static', StaticFiles(directory='src/static'), name='static')


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
@app.exception_handler(status.HTTP_403_FORBIDDEN)
async def root_exception_handler(request: Request, exc: HTTPException):
    """Auto-redirect to login page if user is not logged in"""
    if request.headers.get("HX-Request"):
        return Response(headers={"HX-Redirect": "/auth/signin/"})

    login_url = request.url_for('get_signin')
    return RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Очищаем локацию ошибок, как у вас в коде
    for error in exc.errors():
        error['loc'] = [x for x in error['loc'] if x]

    if request.headers.get("HX-Request"):
        html_content = '<div class="auth-error-container">'
        html_content += '<ul class="auth-error-list">'

        for error in exc.errors():
            loc = [x for x in error.get('loc', []) if x]
            message = error['msg']
            message = re.sub(r'^(Value error|Assertion error|Type error),\s*', '', message)

            if "value is not a valid email" in message:
                message = "is not a valid email address"
            elif "string is too short" in message or "should have at least" in message:
                min_len = error.get('ctx', {}).get('min_length', 6)
                message = f"must be at least {min_len} characters long"
            elif "string is too long" in message:
                max_len = error.get('ctx', {}).get('max_length', 64)
                message = f"must be no more than {max_len} characters long"
            elif "Input should be a valid integer" in message:
                message = f"should be a integer and minimum 6 characters long"

            if error.get('type') == 'no_field_error' or not loc:
                html_content += f'<li class="auth-error-item">{message}</li>'
            else:
                field_name = loc[-1]
                html_content += f'<li class="auth-error-item"><b>{str(field_name).capitalize()}</b> {message}</li>'
        html_content += '</ul></div>'

        return HTMLResponse(content=html_content, status_code=status.HTTP_206_PARTIAL_CONTENT)

    from fastapi.exception_handlers import request_validation_exception_handler
    return await request_validation_exception_handler(request, exc)


@app.get(path='/', response_class=HTMLResponse)
async def get_root(request: Request):
    """Auto-redirect to login page"""
    login_url = request.url_for('get_signin')
    return RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)


app.include_router(login)
app.include_router(register)
app.include_router(profile)
