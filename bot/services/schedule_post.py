import asyncio
import json
from pathlib import Path
from typing import Dict, List, Set

import aiofiles
from aiogram import Bot, html
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.database import RequestsRepo


async def schedule_post(bot: Bot, session_maker: async_sessionmaker) -> None:
    """
    Schedule and send posts to users based on the information stored in a JSON file.

    :param bot: The bot object used to interact with the Telegram API.
    :param session_maker: The asynchronous session maker for database interaction.
    """
    session: AsyncSession
    file_path: Path = Path("/root/Personality/data/data.json")
    id_users: Set = set()
    category_mapping: Dict[int, str] = {
        4: "Молодіжна політика 📚",
        5: "Підтримка психолога 🧘",
        6: "Громадянська освіта 🏛",
        7: "Юридична підтримка ⚖️",
    }

    async with aiofiles.open(file_path, "r", encoding="utf-8") as json_file:
        post_mapping = json.loads(await json_file.read(), parse_int=int)

    async with session_maker() as session:
        repo: RequestsRepo = RequestsRepo(session)
        users: List[tuple] = await repo.users.get_all_users()
        for post_id, post_data in post_mapping.items():
            category = html.bold(
                html.italic(category_mapping.get(post_data["category"]))
            )
            for user in users:
                user_id, subscription_category = user[0], user[post_data["category"]]
                user_post = await repo.posts.get_user_post(
                    user_id=user_id, post_id=post_id
                )
                if not user_post and subscription_category and user_id not in id_users:
                    try:
                        await bot.send_message(
                            chat_id=user_id, text=f"{category}: {post_data['text']}"
                        )
                        await repo.posts.add_post(user_id=user[0], post_id=post_id)
                        await asyncio.sleep(0.05)
                        id_users.add(user_id)
                    except TelegramForbiddenError:
                        continue
