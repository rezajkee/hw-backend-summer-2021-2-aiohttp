from asyncio import Task, create_task
from typing import Optional

from app.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.poll_task = create_task(self.poll())
        self.is_running = True

    async def stop(self):
        if self.is_running and self.poll_task:
            self.is_running = False
            await self.poll_task.cancel()

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            if updates:
                await self.store.bot_manager.handle_updates(updates)
