from datetime import datetime
from typing import Callable, Awaitable, Dict, Any
from cachetools import LRUCache

from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.8) -> None:
        self.limit = limit
        self.cache = LRUCache(maxsize=30)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        current_time = datetime.now().timestamp()
        last_message_time = self.cache.get(user_id, 0)

        if current_time - last_message_time < self.limit:
            return
        else:
            self.cache[user_id] = current_time
        return await handler(event, data)
