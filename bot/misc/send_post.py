import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
from aiogram import Bot, html, types
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache

from bot.database import RequestsRepo


async def send_post(
    message: types.Message,
    bot: Bot,
    text: str,
    repo: RequestsRepo,
    scheduler: Optional[AsyncIOScheduler] = None,
    job_id: Optional[str] = None,
    cache: Optional[LRUCache] = None,
) -> None:
    """
    Send posts to a list of users based on their preferences.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param text: The text content of the post to be sent.
    :param repo: The repository for database requests.
    :param scheduler: (Optional) An asynchronous scheduler for scheduling posts.
                      Defaults to None.
    :param: job_id: (Optional) Identifier for the scheduled job.
                    Defaults to None.
    :param: cache: (Optional) LRUCache for caching data to improve performance.
                   Defaults to None.
    """
    category_mapping: Dict[str, Dict[str, any]] = {
        "Особистість / Молодіжна політика": {
            "category": 4,
            "label": "Молодіжна політика 📚",
        },
        "Особистість / Підтримка психолога": {
            "category": 5,
            "label": "Підтримка психолога 🧘",
        },
        "Особистість / Громадянська освіта": {
            "category": 6,
            "label": "Громадянська освіта 🏛",
        },
        "Особистість / Юридична підтримка": {
            "category": 7,
            "label": "Юридична підтримка ⚖️",
        },
    }
    data: List[tuple] = await repo.users.get_all_users()
    file_path: Path = Path("/root/Personality/data/data.json")
    category: int = category_mapping.get(message.chat.title)["category"]
    label: str = html.bold(
        html.italic(category_mapping.get(message.chat.title)["label"])
    )
    post_id: str = str(uuid.uuid4())

    for user in data:
        try:
            if user[category]:
                await bot.send_message(chat_id=user[0], text=f"{label}: {text}")
                await repo.posts.add_post(user_id=user[0], post_id=post_id)
                await asyncio.sleep(0.05)
        except TelegramForbiddenError:
            continue

    async with aiofiles.open(file_path, "r", encoding="utf-8") as json_file:
        post_mapping = json.loads(await json_file.read())

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
