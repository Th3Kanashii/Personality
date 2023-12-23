from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import LRUCache

from bot.database import RequestsRepo


class UserIdMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.cache = LRUCache(maxsize=10)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        repo: RequestsRepo = data["repo"]

        categories: Dict[str, Dict[str, str]] = {
            "Особистість / Молодіжна політика": {
                "id": "youth_policy",
                "label": "Молодіжна політика 📚",
            },
            "Особистість / Підтримка психолога": {
                "id": "psychologist_support",
                "label": "Підтримка психолога 🧘",
            },
            "Особистість / Юридична підтримка": {
                "id": "legal_support",
                "label": "Юридична підтримка ⚖️",
            },
        }

        key: str = f"{event.chat.id}_{event.message_thread_id}"
        user_id: int = self.cache.get(key)

        if not user_id:
            user_id: int = await repo.users.get_user_id_by_topic(
                topic_id=event.message_thread_id,
                category=categories.get(event.chat.title)["id"],
            )
            self.cache[key] = user_id

        data["user_id"] = user_id
        data["category"] = categories.get(event.chat.title)["label"]
        return await handler(event, data)
