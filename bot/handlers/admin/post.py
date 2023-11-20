from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache

from bot.database import RequestsRepo
from bot.keyboards import cancel_post, cancel_scheduler
from bot.misc import States
from bot.services import send_post

router = Router()


@router.message(Command(commands=["post"]))
async def command_post(
    message: types.Message, state: FSMContext, cache: LRUCache
) -> None:
    """
    Handler the /post command.
    Initiating the process of scheduling and sending posts.

    :param message: The message from Telegram.
    :param state: The FSMContext to manage the conversation state.
    """
    await message.answer(
        text=f"<b>{'Список запланованих розсилок ⌛️' if cache else ''}\n"
        f"{' '.join(value[1] for value in cache.values())}</b>\n\n"
        f"Вкажіть час в форматі YYYY-MM-DD hh:mm ⏰",
        reply_markup=cancel_post(),
    )
    await state.set_state(States.post_datetime)


@router.message(States.post_datetime)
async def post_datetime(
    message: types.Message, bot: Bot, state: FSMContext, cache: LRUCache
) -> None:
    """
    Handler admin input for setting the post date and time or cancelling the process.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param state: The FSMContext to manage the conversation state.
    """
    try:
        target_datetime = datetime.strptime(message.text, "%Y-%m-%d %H:%M")

        current_datetime = datetime.now()

        if target_datetime < current_datetime:
            await bot.edit_message_text(
                text=f"<b>{'Список запланованих розсилок ⌛️' if cache else ''}\n"
                f"{' '.join(value[1] for value in cache.values())}</b>\n\n"
                f"Вкажіть час в форматі YYYY-MM-DD hh:mm ⏰",
                chat_id=message.chat.id,
                message_id=message.message_id - 1,
            )
            await message.answer(
                text="Вибрана дата та час вже минули ⏰",
                reply_markup=cancel_post(),
            )
        else:
            time_difference = (target_datetime - current_datetime).total_seconds()
            await bot.edit_message_text(
                text=f"<b>{'Список запланованих розсилок ⌛️' if cache else ''}\n"
                f"{' '.join(value[1] for value in cache.values())}</b>\n\n"
                f"Вкажіть час в форматі YYYY-MM-DD hh:mm ⏰",
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
            text=f"<b>{'Список запланованих розсилок ⌛️' if cache else ''}\n"
            f"{' '.join(value[1] for value in cache.values())}</b>\n\n"
            f"Вкажіть час в форматі YYYY-MM-DD hh:mm ⏰",
            chat_id=message.chat.id,
            message_id=message.message_id - 1,
        )
        await message.answer(
            text="Неправильно введені дані ❌\n"
            "Використовуйте формат YYYY-MM-DD hh:mm ⏰\n"
            "Спробуйте ще раз 🔄",
            reply_markup=cancel_post(),
        )
        for id in range(0, 2):
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id - id
            )


@router.message(States.post)
async def post(
    message: types.Message,
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
    data = await state.get_data()
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
        minutes, seconds = divmod(remainder, 60)

        job_id = f"{message.from_user.id}{message.date.timestamp()}"
        unique_id = f"{message.chat.title} - {data['time']}"
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
    callback: types.CallbackQuery,
    cache: LRUCache,
    scheduler: AsyncIOScheduler,
) -> None:
    """
    Handler the callback from admin who wants to cancel a scheduled notification.

    :param callback: The callback query from the admin.
    """
    job_id = callback.message.text.split("id: ")[-1]
    new_text = callback.message.text.split("\n\n")[0]
    scheduler.remove_job(job_id)
    del cache[job_id]
    await callback.message.unpin()
    await callback.message.edit_text(
        text=f"{new_text}\n\n" f"<b>Сповіщення скасовано ❌</b>"
    )


@router.callback_query(F.data == "cancel_post")
async def callback_cancel_post(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    await callback.message.edit_text(text="<b>Сповіщення скасовано ❌</b>")
    await state.clear()


@router.callback_query(F.data == "next")
async def callback_next_post(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        text="Надішліть текст для сповіщення ✍️",
        reply_markup=cancel_post(back=True),
    )
    await state.update_data(dict(datetime=None, time=None))
    await state.set_state(States.post)


@router.callback_query(F.data == "back")
async def callback_back_post(
    callback: types.CallbackQuery, state: FSMContext, cache: LRUCache
) -> None:
    await callback.message.edit_text(
        text=f"<b>{'Список запланованих розсилок ⌛' if cache else ''}\n"
        f"{' '.join(value[1] for value in cache.values())}</b>\n\n"
        f"Вкажіть час в форматі YYYY-MM-DD hh:mm ⏰",
        reply_markup=cancel_post(),
    )
    await state.set_state(States.post_datetime)
