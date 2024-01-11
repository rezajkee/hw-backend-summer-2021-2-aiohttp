import random
import typing
from typing import List, Optional

from aiohttp.client import ClientSession
from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateMessage, UpdateObject

if typing.TYPE_CHECKING:
    from app.store.vk_api.poller import Poller
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None

        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.ts: Optional[int] = None

        self.poller: Optional["Poller"] = None

    async def connect(self, app: "Application"):
        from app.store.vk_api.poller import Poller

        self.session = ClientSession()
        await self._get_long_poll_service()
        # await self.send_message(message=Message(
        #     text='Hello',
        #     user_id=35390164
        # ))
        self.poller = Poller(self.app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session and not self.session.closed:
            await self.session.close()
        if self.poller and self.poller.is_running:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: Optional[str], params: dict) -> str:
        if method:
            url = host + method + "?"
        else:
            url = host + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        url = self._build_query(
            host='https://api.vk.com/method/',
            method='groups.getLongPollServer',
            params={
                'access_token': self.app.config.bot.token,
                'group_id': self.app.config.bot.group_id,
            }
        )
        async with self.session.get(url) as response:
            data = (await response.json())['response']
            self.key = data['key']
            self.server = data['server']
            self.ts = data['ts']

    async def poll(self) -> List[Update]:
        url = self._build_query(
            self.server,
            method='',
            params={
                'act': 'a_check',
                'key': self.key,
                'ts': self.ts,
                'wait': 25
            }
        )

        async with self.session.get(url) as response:
            data = await response.json()
            updates = []
            self.ts = data['ts']
            for update in data.get('updates', []):
                if update['type'] == 'message_new':
                    updates.append(
                        Update(
                            type='message_new',
                            object=UpdateObject(
                                message=UpdateMessage(
                                    from_id=update['object']['message']['from_id'],
                                    text=update['object']['message']['text'],
                                    id=update['object']['message']['id'],
                                )
                            )
                        )
                    )

        return updates

    async def send_message(self, message: Message) -> None:
        url = self._build_query(
            host='https://api.vk.com/method/',
            method='messages.send',
            params={
                'user_id': message.user_id,
                'message': message.text,
                'access_token': self.app.config.bot.token,
                'random_id': random.randint(1, 9999999999)
            }
        )
        async with self.session.get(url):
            pass
