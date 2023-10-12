import asyncio

from aiogram import types, Bot
from aiogram.exceptions import TelegramForbiddenError

from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def send_notification(message: types.Message,
                            bot: Bot,
                            data: list,
                            scheduler: AsyncIOScheduler = None,
                            media: list = None) -> None:
    """


    :param bot:
    :param message:
    :param data:
    :param scheduler:
    :param media:
    """
    category_mapping = {
        "Молодіжна політика": 4,
        "Підтримка психолога": 5,
        "Громадянська освіта": 6,
        "Юридична підтримка": 7
    }
    category = category_mapping.get(message.chat.title)
    for user in data:
        if user[category]:
            try:
                if media:
                    await bot.send_media_group(chat_id=user[0],
                                               media=media)
                else:
                    await message.copy_to(chat_id=user[0])
                await asyncio.sleep(0.01)
            except TelegramForbiddenError:
                continue
    if scheduler:
        scheduler.shutdown()
