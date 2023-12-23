import asyncio
from typing import Final, List

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

from bot.database import RequestsRepo
from bot.filters import Admin

router: Final[Router] = Router(name=__name__)
router.message.filter(Admin())


@router.message(Command("all", prefix="!"))
async def command_all(message: types.Message, bot: Bot, repo: RequestsRepo) -> None:
    """
    Handler to command /all
    Send messages to all users

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param repo: The repository for database requests.
    """
    if not message.text or len(message.text) <= 4:
        await message.answer(text="Спробуйте ще раз 🔄")
        return

    users: List[tuple] = await repo.users.get_all_users()

    for user in users:
        try:
            await bot.send_message(chat_id=user[0], text=f"{message.text[4:]}")
            await asyncio.sleep(0.05)
        except TelegramBadRequest:
            continue
    await message.answer(text="Сповіщення успішно надіслано ✅")
