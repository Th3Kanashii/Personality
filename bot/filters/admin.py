from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import Config


class Admin(BaseFilter):
    def __init__(self, command: bool = True) -> None:
        self.command = command

    async def __call__(self, message: Message, config: Config) -> bool:
        is_admin: bool = message.from_user.id in config.tg_bot.admins
        is_super_chat: bool = message.chat.id == config.tg_bot.civic_education
        is_admin_chat: bool = message.chat.id in config.tg_bot.all_groups
        is_thread_message: bool = message.message_thread_id is not None

        if self.command:
            return is_admin and not is_thread_message and is_admin_chat

        if is_super_chat and is_admin:
            return True

        return is_admin and is_thread_message and is_admin_chat
