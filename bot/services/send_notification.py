import asyncio
import json
import uuid

from aiogram import types, Bot
from aiogram.exceptions import TelegramForbiddenError

from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def send_notification(message: types.Message,
                            bot: Bot,
                            data: list,
                            scheduler: AsyncIOScheduler = None) -> None:
    """
    Send notifications to a list of users based on their preferences.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param data: The list users.
    :param scheduler:
    """
    category_mapping = {
        "Особистість / Молодіжна політика": 4,
        "Особистість / Підтримка психолога": 5,
        "Особистість / Громадянська освіта": 6,
        "Особистість / Юридична підтримка": 7
    }
    category = category_mapping.get(message.chat.title)
    notification_token = str(uuid.uuid4())
    user_ids = list()

    for user in data:
        try:
            if user[category]:
                await message.copy_to(chat_id=user[0])
                user_ids.append(user[0])
                await asyncio.sleep(0.01)
        except TelegramForbiddenError:
            continue

    with open("/root/Personality/data.json", "r", encoding="utf-8") as json_file:
        token_message_mapping = json.load(json_file)

    token_message_mapping[notification_token] = [message.text, category, user_ids]

    with open("/root/Personality/data.json", "w", encoding="utf-8") as json_file:
        json.dump(token_message_mapping, json_file, ensure_ascii=False, indent=4)

    if scheduler:
        await bot.unpin_chat_message(chat_id=message.chat.id,
                                     message_id=message.message_id+1)
        await bot.edit_message_text(text="Сповіщення надіслано",
                                    chat_id=message.chat.id,
                                    message_id=message.message_id+1)
        scheduler.shutdown()
