from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler) -> None:
        super().__init__()
        self.scheduler = scheduler
        self.cache = LRUCache(maxsize=50)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["scheduler"] = self.scheduler
        data["cache"] = self.cache
        return await handler(event, data)
