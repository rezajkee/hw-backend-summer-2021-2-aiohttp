from aiohttp.web_exceptions import HTTPConflict
from aiohttp_apispec import request_schema
from app.quiz.schemes import ThemeListSchema, ThemeSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    async def post(self):
        title = self.data['title']

        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            raise HTTPConflict

        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data={'theme': ThemeSchema().dump(theme)})


class ThemeListView(AuthRequiredMixin, View):
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({'themes': themes}))


class QuestionAddView(View):
    async def post(self):
        raise NotImplementedError


class QuestionListView(View):
    async def get(self):
        raise NotImplementedError
