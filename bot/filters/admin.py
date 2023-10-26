from aiogram.filters import BaseFilter
from aiogram.types import Message


class Admin(BaseFilter):
    def __init__(self, admins: list, command: bool = True) -> None:
        self.admins = admins
        self.command = command

    async def __call__(self, message: Message) -> bool:
        if self.command:
            return message.from_user.id in self.admins and message.message_thread_id is None
        return message.from_user.id in self.admins
