from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema
from aiohttp_session import new_session
from app.admin.schemes import AdminResponseSchema, AdminSchema
from app.web.app import View
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    async def post(self):
        email = self.data['email']
        password = self.data['password']
        admin = await self.store.admins.get_by_email(email)
        if not admin:
            raise HTTPForbidden

        if not admin.check_password(password):
            raise HTTPForbidden

        session = await new_session(self.request)
        raw_admin = AdminResponseSchema().dump(admin)
        session['admin'] = raw_admin
        return json_response(data={'admin': raw_admin})


class AdminCurrentView(View):
    async def get(self):
        if not self.request.admin:
            raise HTTPUnauthorized

        return json_response(data={'admin': AdminResponseSchema().dump(self.request.admin)})
