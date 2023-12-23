from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: Union[int, float] = 0.5) -> None:
        self.cache: Dict[str, TTLCache] = {"default": TTLCache(maxsize=100, ttl=limit)}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None and throttling_key in self.cache:
            if event.chat.id in self.cache[throttling_key]:
                return
            else:
                self.cache[throttling_key][event.chat.id] = None
        return await handler(event, data)
