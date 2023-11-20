from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, user

from bot.database import RequestsRepo


class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: user.User = data.get("event_from_user")
        repo: RequestsRepo = data["repo"]

        if not await repo.users.get_user(user_id=tg_user.id):
            await repo.users.add_user(
                user_id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
            )

        return await handler(event, data)
