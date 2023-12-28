from datetime import datetime
from typing import Any, Dict, Final

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache

from bot.database import RequestsRepo
from bot.keyboards import cancel_post, cancel_scheduler
from bot.misc import States, send_post

router: Final[Router] = Router(name=__name__)


def scheduled_post(cache: LRUCache) -> str:
    """
    Generates a formatted string representing the list of scheduled posts.

    :param cache: The LRUCache to store information about scheduled jobs.
    :return: A string displaying the scheduled posts and a prompt for specifying the time.
    """
    return (
        f"<b>{'Список запланованих розсилок ⌛️' if cache else ''}\n"
        f"{''.join(value[1] for value in cache.values())}</b>\n\n"
        f"Вкажіть час в форматі DD/MM/hh:mm ⏰"
    )


@router.message(Command("post"))
async def command_post(message: Message, state: FSMContext, cache: LRUCache) -> None:
    """
    Handler the /post command.
    Initiating the process of scheduling and sending posts.

    :param message: The message from Telegram.
    :param state: The FSMContext to manage the conversation state.
    """
    await message.answer(
        text=scheduled_post(cache=cache),
        reply_markup=cancel_post(),
    )
    await state.set_state(States.post_datetime)


@router.message(States.post_datetime)
async def post_datetime(
    message: Message, bot: Bot, state: FSMContext, cache: LRUCache
) -> None:
    """
    Handler admin input for setting the post date and time or cancelling the process.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param state: The FSMContext to manage the conversation state.
    """
    try:
        target_datetime = datetime.strptime(message.text, "%d/%m/%H:%M")

        current_datetime = datetime.now()

        # Format current_datetime to match the format of target_datetime
        current_datetime_str = current_datetime.strftime("%d/%m/%H:%M")
        current_datetime = datetime.strptime(current_datetime_str, "%d/%m/%H:%M")

        if target_datetime < current_datetime:
            await bot.edit_message_text(
                text=scheduled_post(cache=cache),
                chat_id=message.chat.id,
                message_id=message.message_id - 1,
            )
            await message.answer(
                text="Вибрана дата та час вже минули ⏰",
                reply_markup=cancel_post(),
            )
        else:
            time_difference: float = (
                target_datetime - current_datetime
            ).total_seconds()
            await bot.edit_message_text(
                text=scheduled_post(cache=cache),
                chat_id=message.chat.id,
                message_id=message.message_id - 1,
            )
            await message.answer(
                text="Надішліть текст для сповіщення ✍️",
                reply_markup=cancel_post(back=True),
            )
            await state.update_data(dict(datetime=time_difference, time=message.text))
            await state.set_state(States.post)
    except ValueError:
        await bot.edit_message_text(
            text=scheduled_post(cache=cache),
            chat_id=message.chat.id,
            message_id=message.message_id - 1,
        )
        await message.answer(
            text="Неправильно введені дані ❌\n"
            "Використовуйте формат DD/MM/hh:mm ⏰\n"
            "Спробуйте ще раз 🔄",
            reply_markup=cancel_post(),
        )
        for id in range(0, 2):
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id - id
            )


@router.message(States.post)
async def post(
    message: Message,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
    scheduler: AsyncIOScheduler,
    cache: LRUCache,
) -> None:
    """
    Handler admin input for setting the post message, scheduling.

    :param message: The message from Telegram.
    :param state: The FSMContext to manage the conversation state.
    :param bot: The bot object used to interact with the Telegram API.
    :param repo: The repository for database requests.
    """
    data: Dict[str, Any] = await state.get_data()
    if not message.text:
        await message.answer(
            text="Надішліть текст для сповіщення ✍️",
            reply_markup=cancel_post(back=True),
        )
        for id in range(0, 2):
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id - id
            )
    elif data["datetime"] is None:
        await send_post(message=message, bot=bot, text=message.text, repo=repo)
        await message.answer(
            text=f"{message.text}\n\n" f"<b>Сповіщення надіслано ✅</b>\n",
        )
        await state.clear()
        for id in range(0, 2):
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id - id
            )
    else:
        days, remainder = divmod(data["datetime"], 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        job_id: str = f"{message.from_user.id}{message.date.timestamp()}"
        unique_id: str = f"{message.chat.title.split('/')[1]} - {data['time']}\n"
        scheduler.add_job(
            func=send_post,
            args=(message, bot, message.text, repo, scheduler, job_id, cache),
            trigger="interval",
            seconds=data["datetime"],
            id=job_id,
        )

        cache[job_id] = [job_id, unique_id]

        await message.answer(
            text=f"{message.text}\n\n"
            f"<b>Сповіщення заплановано ⌛\n"
            f"Відправлення через {int(days)} днів, {int(hours)} годин, {int(minutes)} хвилин\n"
            f"id: {job_id}</b>",
            reply_markup=cancel_scheduler(),
        )
        await bot.pin_chat_message(
            chat_id=message.chat.id, message_id=message.message_id + 1
        )
        await state.clear()

        for id in range(0, 4):
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id - id
            )


@router.callback_query(F.data == "cancel")
async def callback_cancel_scheduler(
    callback: CallbackQuery,
    cache: LRUCache,
    scheduler: AsyncIOScheduler,
) -> None:
    """
    Handler the callback from admin who wants to cancel a scheduled notification.

    :param callback: The callback query from the admin.
    :param cache: The LRUCache to store information about scheduled jobs.
    :param scheduler: The AsyncIOScheduler to manage scheduled tasks.
    """
    job_id: str = callback.message.text.split("id: ")[-1]
    new_text: str = callback.message.text.split("\n\n")[0]

    scheduler.remove_job(job_id)
    del cache[job_id]

    await callback.message.unpin()
    await callback.message.edit_text(
        text=f"{new_text}\n\n" f"<b>Сповіщення скасовано ❌</b>"
    )


@router.callback_query(F.data == "cancel_post")
async def callback_cancel_post(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler the callback from an admin who wants to cancel a post creation.

    :param callback: The callback query from the admin.
    :param state: The FSMContext to manage the conversation state.
    """
    await callback.message.edit_text(text="<b>Сповіщення скасовано ❌</b>")
    await state.clear()


@router.callback_query(F.data == "next")
async def callback_next_post(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler the callback from an admin to proceed to the next step in post creation.

    :param callback: The callback query from the admin.
    :param state: The FSMContext to manage the conversation state.
    """
    await callback.message.edit_text(
        text="Надішліть текст для сповіщення ✍️",
        reply_markup=cancel_post(back=True),
    )
    await state.update_data(dict(datetime=None, time=None))
    await state.set_state(States.post)


@router.callback_query(F.data == "back")
async def callback_back_post(
    callback: CallbackQuery, state: FSMContext, cache: LRUCache
) -> None:
    """
    Handler the callback from an admin to go back to the previous step in post creation.

    :param callback: The callback query from the admin.
    :param state: The FSMContext to manage the conversation state.
    :param cache: The LRUCache to store information about scheduled jobs.
    """
    await callback.message.edit_text(
        text=scheduled_post(cache=cache),
        reply_markup=cancel_post(),
    )
    await state.set_state(States.post_datetime)
