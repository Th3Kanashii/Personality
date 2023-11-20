from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import Config


class Admin(BaseFilter):
    def __init__(self, command: bool = True) -> None:
        self.command = command

    async def __call__(self, message: Message, config: Config) -> bool:
        if self.command:
            return (
                message.from_user.id in config.tg_bot.admins
                and message.message_thread_id is None
            )
        return (
            message.from_user.id in config.tg_bot.admins
            and message.message_thread_id is not None
        )
