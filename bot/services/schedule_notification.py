import json
import asyncio

from typing import List, Set

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.database import RequestsRepo


async def schedule_notification(bot: Bot,
                                session_maker: async_sessionmaker) -> None:
    """
    Schedule and send notifications to users based on the information stored in a JSON file.

    :param bot: The bot object used to interact with the Telegram API.
    :param session_maker:
    """
    session: AsyncSession
    async with session_maker() as session:
        repo = RequestsRepo(session)
        users = await repo.users.get_all_users()

    json_file_path = "/root/Personality/data.json"
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        message = json.load(json_file)

    ids: Set = set()
    user_ids: List[int] = []

    for key, value in message.items():
        for user in users:
            try:
                user_id, user_field = user[0], user[value[1]]
                if user_id not in value[2] and user_field and user_id not in ids:
                    await bot.send_message(chat_id=user_id, text=value[0])
                    ids.add(user_id)
                    user_ids.append(user_id)
                    await asyncio.sleep(0.01)
            except TelegramForbiddenError:
                continue
        message[key] = [value[0], value[1], value[2] + user_ids]
        user_ids.clear()

    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(message, json_file, ensure_ascii=False, indent=4)
    await session.close()
