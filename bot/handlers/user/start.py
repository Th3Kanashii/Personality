from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.database import DataAccessObject
from bot.keyboards import start


router = Router()


@router.message(CommandStart())
async def _start(message: types.Message,
                 dao: DataAccessObject) -> None:
    """
    Handler to /start commands with user.

    :param message: The message from Telegram.
    :param dao: The DataAccessObject for database access.
    """
    subscriptions = await dao.get_user_subscriptions(user_id=message.from_user.id)
    await message.answer(text=f"Привіт, {message.from_user.first_name}, обери бажаний розділ",
                         reply_markup=start(subscriptions))
