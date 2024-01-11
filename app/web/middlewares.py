import json
import typing

from aiohttp.web_exceptions import HTTPForbidden, HTTPUnprocessableEntity
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session
from app.admin.models import Admin
from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def auth_middleware(request: "Request", handler):
    session = await get_session(request)
    if request.cookies.get('AIOHTTP_SESSION') and not session.get('admin'):
        raise HTTPForbidden
    if session.get('admin'):
        request.admin = Admin(
            id=session['admin']['id'],
            email=session['admin']['email'],
        )
    else:
        request.admin = None
    return await handler(request)


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    # TODO: обработать все исключения-наследники HTTPException и отдельно Exception, как server error
    #  использовать текст из HTTP_ERROR_CODES


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
