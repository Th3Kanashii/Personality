from typing import Callable, Awaitable, Dict, Any

from cachetools import LRUCache

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.database import DataAccessObject


class UserIdMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.cache = LRUCache(maxsize=10)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        dao: DataAccessObject = data["dao"]

        key = f"{event.chat.id}_{event.message_thread_id}"
        user_id = self.cache.get(key)

        if not user_id:
            categories = {
                "Молодіжна політика": "youth_policy",
                "Підтримка психолога": "psychologist_support",
                "Громадянська освіта": "civic_education",
                "Юридична підтримка": "legal_support"
            }
            user_id = await dao.get_user_id_by_topic(topic_id=event.message_thread_id,
                                                     category=categories.get(event.chat.title))
            self.cache[key] = user_id

        data["user_id"] = user_id
        return await handler(event, data)
