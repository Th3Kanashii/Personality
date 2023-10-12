from aiogram import types, Router
from aiogram.filters import Command

from bot.database import DataAccessObject

router = Router()


@router.message(Command(commands=["ban"]))
async def ban_user(message: types.Message,
                   dao: DataAccessObject) -> None:
    await dao.ban_user(topic_id=message.message_thread_id,
                       category=message.chat.title)
    await message.answer("Користувача заблоковано!")
