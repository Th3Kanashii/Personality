import asyncio
import json
import uuid

import aiofiles
from aiogram import Bot, types
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache

from bot.database import RequestsRepo


async def send_post(
    message: types.Message,
    bot: Bot,
    text: str,
    repo: RequestsRepo,
    scheduler: AsyncIOScheduler = None,
    job_id: str = None,
    cache: LRUCache = None,
) -> None:
    """
    Send posts to a list of users based on their preferences.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param data: The list users.
    :param scheduler:
    """
    category_mapping = {
        "Особистість / Молодіжна політика": 4,
        "Особистість / Підтримка психолога": 5,
        "Особистість / Громадянська освіта": 6,
        "Особистість / Юридична підтримка": 7,
    }
    data = await repo.users.get_all_users()
    file_path = "/root/Personality/data.json"
    category = category_mapping.get(message.chat.title)
    post_id = str(uuid.uuid4())

    for user in data:
        try:
            if user[category]:
                await bot.send_message(chat_id=user[0], text=text)
                await repo.posts.add_post(user_id=user[0], post_id=post_id)
                await asyncio.sleep(0.01)
        except TelegramForbiddenError:
            continue

    async with aiofiles.open(file_path, "r", encoding="utf-8") as json_file:
        post_mapping = await json_file.read()
        post_mapping = json.loads(post_mapping)

    post_mapping[post_id] = {"text": text, "category": category}

    async with aiofiles.open(file_path, "w", encoding="utf-8") as json_file:
        await json_file.write(json.dumps(post_mapping, ensure_ascii=False, indent=4))

    if scheduler:
        await bot.unpin_chat_message(
            chat_id=message.chat.id, message_id=message.message_id + 1
        )
        await bot.edit_message_text(
            text=f"{text}\n\n" f"<b>Сповіщення надіслано ✅</b>\n",
            chat_id=message.chat.id,
            message_id=message.message_id + 1,
        )

        scheduler.remove_job(job_id=job_id)
        del cache[job_id]
