from typing import Dict, Final, List

from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.keyboards import start
from bot.middlewares import RegisterUserMiddleware, ThrottlingMiddleware

flags: Final[Dict[str, str]] = {"throttling_key": "default"}

router: Final[Router] = Router(name=__name__)

router.message.middleware(RegisterUserMiddleware())
router.message.middleware(ThrottlingMiddleware(limit=3))


@router.message(CommandStart(), flags=flags)
async def command_start(message: types.Message, subscriptions: List[str]) -> None:
    """
    Handler to /start commands with user.

    :param message: The message from Telegram.
    :param subscriptions: A list of user subscriptions.
    """
    await message.answer(
        text=f"Привіт, {message.from_user.first_name}, обери бажаний розділ",
        reply_markup=start(subscriptions),
    )
