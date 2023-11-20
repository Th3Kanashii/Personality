import asyncio
import json
from typing import Literal, Set

import aiofiles
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.database import RequestsRepo


async def schedule_post(bot: Bot, session_maker: async_sessionmaker) -> None:
    """
    Schedule and send posts to users based on the information stored in a JSON file.

    :param bot: The bot object used to interact with the Telegram API.
    :param session_maker:
    """
    session: AsyncSession
    file_path: Literal[
        "/root/Personality/data.json"
    ] = "/root/Personality/data.json"
    id_users: Set = set()

    async with session_maker() as session:
        repo = RequestsRepo(session)
        users = await repo.users.get_all_users()

    async with aiofiles.open(file_path, "r", encoding="utf-8") as json_file:
        post_mapping = await json_file.read()
        post_mapping = json.loads(post_mapping)

    for post_id, post_data in post_mapping.items():
        for user in users:
            user_id, subscription_category = user[0], user[post_data["category"]]
            user_post = await repo.posts.get_user_post(user_id=user_id, post_id=post_id)
            if not user_post and subscription_category and user_id not in id_users:
                try:
                    await bot.send_message(chat_id=user_id, text=post_data["text"])
                    await repo.posts.add_post(user_id=user[0], post_id=post_id)
                    await asyncio.sleep(0.01)
                    id_users.add(user_id)
                except TelegramForbiddenError:
                    continue

    await session.close()
