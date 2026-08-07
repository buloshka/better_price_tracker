import re
import logging

from fastapi import FastAPI, Request, status, HTTPException

from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from src.routers.auth import login, register
from src.routers.profile import profile
from src.utils.templates import source


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("alembic").setLevel(logging.INFO)


app = FastAPI(title='Price Tracker')
app.mount('/static', StaticFiles(directory='src/static'), name='static')


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def session_expired_exception_handler(request: Request, exc: HTTPException):
    if request.headers.get("HX-Request"):
        return Response(headers={"HX-Redirect": "/auth/signin/"})

    login_url = request.url_for('get_signin')

    return source.TemplateResponse(
        request=request,
        name='error_generic.html',
        context={
            'title': 'Session Expired',
            'error_class': 'warning-type',
            'header': 'Session Expired',
            'description': 'Your session has expired or you are not logged in. Please log in again to continue working with your trackers.',
            'button_text': 'OK, Log In',
            'action_url': str(login_url)
        },
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(status.HTTP_403_FORBIDDEN)
async def forbidden_exception_handler(request: Request, exc: HTTPException):
    if request.headers.get("HX-Request"):
        return Response(status_code=200, headers={"HX-Trigger": "..."})

    return source.TemplateResponse(
        request=request,
        name='error_generic.html',
        context={
            'title': 'Access Denied',
            'error_class': 'info-type',
            'header': 'Access Denied',
            'description': 'This profile does not belong to you. Please log in with the correct credentials.',
            'button_text': 'Go to Login',
            'action_url': '/auth/signin/'
        },
        status_code=status.HTTP_403_FORBIDDEN
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return source.TemplateResponse(
        request=request,
        name='error_generic.html',
        context={
            'title': 'Page Not Found',
            'error_class': '',
            'header': '404 - Not Found',
            'description': 'The profile or tracker you are looking for does not exist or has been deleted.',
            'button_text': 'Back to Home',
            'action_url': '/'
        },
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.headers.get("HX-Request"):
        html_content = '<div class="auth-error-container">'
        html_content += '<ul class="auth-error-list">'

        route = request.scope.get("route")
        route_fields = {}
        if route and hasattr(route, "dependant"):
            for param in route.dependant.body_params + route.dependant.query_params:
                route_fields[param.name] = param

        model_name = getattr(exc, 'model_name', None)
        model_cls = None
        if model_name:
            import sys
            for mod_name, mod in list(sys.modules.items()):
                if "schemas" in mod_name and hasattr(mod, model_name):
                    model_cls = getattr(mod, model_name)
                    break

        for error in exc.errors():
            loc = [x for x in error.get('loc', []) if x]
            message = error['msg']
            raw_field_name = loc[-1] if loc else None

            if error.get('type') == 'no_field_error' or not raw_field_name:
                message = re.sub(r'^(Value error|Assertion error|Type error),\s*', '', message)
                html_content += f'<li class="auth-error-item">{message}</li>'
                continue

            search_key = str(raw_field_name).lower()
            display_field_name = search_key.capitalize()
            custom_message = None

            if search_key in route_fields:
                param_obj = route_fields[search_key]

                field_info = getattr(param_obj, 'field_info', param_obj)

                if field_info and getattr(field_info, 'title', None):
                    display_field_name = field_info.title
                if field_info and getattr(field_info, 'description', None):
                    custom_message = field_info.description

            if not custom_message and model_cls and search_key in model_cls.model_fields:
                f_info = model_cls.model_fields[search_key]
                if f_info.title:
                    display_field_name = f_info.title
                if f_info.description:
                    custom_message = f_info.description
            if custom_message:
                message = custom_message
            else:
                message = re.sub(r'^(Value error|Assertion error|Type error),\s*', '', message).lower()
                if "input should be a valid integer" in message:
                    message = "must be a valid integer number"

            html_content += f'<li class="auth-error-item"><b>{display_field_name}</b> {message}</li>'
        html_content += '</ul></div>'
        return HTMLResponse(content=html_content, status_code=status.HTTP_206_PARTIAL_CONTENT)
    return source.TemplateResponse(
        request=request,
        name='error_generic.html',
        context={
            'title': 'Unprocessable Error',
            'error_class': '',
            'header': '422 - Unprocessable Entity',
            'description': 'Oops, something went wrong...',
            'button_text': 'Back',
            'action_url': 'javascript:history.back()'
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.get(path='/', response_class=HTMLResponse)
async def get_root(request: Request):
    """Auto-redirect to login page"""
    login_url = request.url_for('get_signin')
    return RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)


app.include_router(login)
app.include_router(register)
app.include_router(profile)
