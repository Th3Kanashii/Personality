from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, user
from aiogram.utils.markdown import hlink

from bot.database import RequestsRepo
from bot.keyboards import start, cancel_subscription


class TopicMiddleware(BaseMiddleware):
    @staticmethod
    async def create_topic(chat_id: str,
                           bot: Bot,
                           message: Message,
                           repo: RequestsRepo) -> None:
        """
        Create a new forum topic and associated chat for a user.

        :param chat_id: The chat ID where the topic and chat will be created.
        :param bot: The bot object used to interact with the Telegram API.
        :param message: The message from Telegram.
        :param repo: The repository for database requests.
        """
        topic_id = await bot.create_forum_topic(chat_id=chat_id,
                                                name=message.from_user.first_name)
        await message.answer(text="Привіт! Наш спеціаліст-волонтер радо відповість на всі запитання в час від 13:00 - "
                                  "14:00 або з 19:00 - 20:00. Не хвилюйся, ми додамо максимум зусиль та знань, "
                                  "щоб проконсультувати тебе якісно.",
                             reply_markup=cancel_subscription())
        await bot.send_message(chat_id=chat_id,
                               text=f"Чат з користувачем {hlink(message.from_user.first_name, message.from_user.url)}"
                                    f" (@{message.from_user.username}) створено!",
                               message_thread_id=topic_id.message_thread_id)
        await message.copy_to(chat_id=chat_id,
                              message_thread_id=topic_id.message_thread_id)
        await repo.users.add_topic_id(user_id=message.from_user.id,
                                      topic_id=topic_id.message_thread_id)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        tg_user: user.User = data.get("event_from_user")
        repo: RequestsRepo = data["repo"]
        config = data["config"]

        user_object = await repo.users.get_user(user_id=tg_user.id)
        active_category = user_object.active_category
        user_topic = f"{active_category}_topic"

        if active_category == "civic_education":
            await event.answer(text="Спілкування з волонтером не доступно",
                               reply_markup=cancel_subscription())

        elif not active_category:
            subscriptions = await repo.users.get_user_subscriptions(user_id=tg_user.id)
            await event.answer(text="Будь ласка оберіть категорію",
                               reply_markup=start(subscriptions))
            return

        elif hasattr(user_object, user_topic) and not getattr(user_object, user_topic):
            chat_id = getattr(config.tg_bot, user_object.active_category)
            await self.create_topic(chat_id=chat_id,
                                    bot=data["bot"],
                                    message=event,
                                    repo=repo)
            return

        else:
            data["chat_id"] = getattr(config.tg_bot, active_category)
            data["topic_id"] = getattr(user_object, user_topic)
            return await handler(event, data)
