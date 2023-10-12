from typing import Callable, Awaitable, Dict, Any

from cachetools import LRUCache

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, user
from aiogram.utils.markdown import hlink

from bot.database import DataAccessObject


class TopicMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.cache = LRUCache(maxsize=10)

    @staticmethod
    async def create_topic(chat_id: str,
                           bot: Bot,
                           message: Message,
                           dao: DataAccessObject) -> None:
        """
        Create a new forum topic and associated chat for a user.

        :param chat_id: The chat ID where the topic and chat will be created.
        :param bot: The bot object used to interact with the Telegram API.
        :param message: The message from Telegram.
        :param dao: The DataAccessObject for database access.
        """
        topic_id = await bot.create_forum_topic(chat_id=chat_id,
                                                name=message.from_user.first_name)
        await bot.send_message(chat_id=chat_id,
                               text=f"Чат з користувачем {hlink(message.from_user.first_name, message.from_user.url)}"
                                    f" (@{message.from_user.username}) створено!",
                               message_thread_id=topic_id.message_thread_id)
        await message.copy_to(chat_id=chat_id,
                              message_thread_id=topic_id.message_thread_id)
        await dao.add_topic_id(user_id=message.from_user.id,
                               topic_id=topic_id.message_thread_id)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        tg_user: user.User = data.get("event_from_user")
        dao: DataAccessObject = data["dao"]
        config = data["config"]

        user_object = await dao.get_user(user_id=tg_user.id)
        active_category = user_object.active_category
        user_topic = f"{active_category}_topic"

        if hasattr(user_object, user_topic) and not getattr(user_object, user_topic):
            chat_id = getattr(config.tg_bot, user_object.active_category)
            await self.create_topic(chat_id=chat_id,
                                    bot=data["bot"],
                                    message=event,
                                    dao=dao)
            return

        elif not active_category:
            await event.answer(text="Будь ласка оберіть категорію")
            return

        else:
            data["chat_id"] = getattr(config.tg_bot, active_category)
            data["topic_id"] = getattr(user_object, user_topic)
            return await handler(event, data)
