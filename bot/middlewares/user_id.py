from typing import Callable, Awaitable, Dict, Any

from cachetools import LRUCache

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.database import RequestsRepo


class UserIdMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.cache = LRUCache(maxsize=10)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        repo: RequestsRepo = data["repo"]

        categories = {
            "Особистість / Молодіжна політика": ["youth_policy", "Молодіжна політика 📚:"],
            "Особистість / Підтримка психолога": ["psychologist_support", "Підтримка психолога 🧘:"],
            "Особистість / Юридична підтримка": ["legal_support", "Юридична підтримка ⚖️:"]
        }
        key = f"{event.chat.id}_{event.message_thread_id}"
        user_id = self.cache.get(key)

        if not user_id:
            user_id = await repo.users.get_user_id_by_topic(topic_id=event.message_thread_id,
                                                            category=categories.get(event.chat.title)[0])
            self.cache[key] = user_id

        data["user_id"] = user_id
        data["category"] = categories.get(event.chat.title)[1]
        return await handler(event, data)
