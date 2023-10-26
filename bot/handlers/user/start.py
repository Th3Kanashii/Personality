from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.database import RequestsRepo
from bot.keyboards import start

router = Router()


@router.message(CommandStart())
async def command_start(message: types.Message,
                        repo: RequestsRepo) -> None:
    """
    Handler to /start commands with user.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    subscriptions = await repo.users.get_user_subscriptions(user_id=message.from_user.id)
    await message.answer(text=f"Привіт, {message.from_user.first_name}, обери бажаний розділ",
                         reply_markup=start(subscriptions))
