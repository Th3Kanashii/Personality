from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache
from datetime import datetime

from bot.database import RequestsRepo
from bot.keyboards import cancel_notification, cancel_scheduler
from bot.misc import States, send_notification

router = Router()
cache = LRUCache(maxsize=50)


@router.message(Command(commands=["notification"]))
async def command_notification(message: types.Message,
                               state: FSMContext) -> None:
    """
    Handler the /notification command.
    Initiating the process of scheduling and sending notifications.

    :param message: The message from Telegram.
    :param state: The FSMContext to manage the conversation state.
    """
    await message.answer(text="Вкажіть час в форматі YYYY-MM-DD hh:mm",
                         reply_markup=cancel_notification())
    await state.set_state(States.notification_datetime)


@router.message(States.notification_datetime)
async def notification_datetime(message: types.Message,
                                bot: Bot,
                                state: FSMContext) -> None:
    """
    Handler admin input for setting the notification date and time or cancelling the process.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param state: The FSMContext to manage the conversation state.
    """
    try:
        target_datetime = datetime.strptime(message.text, "%Y-%m-%d %H:%M")

        current_datetime = datetime.now()

        if target_datetime < current_datetime:
            await bot.edit_message_text(text="Вкажіть час в форматі YYYY-MM-DD hh:mm",
                                        chat_id=message.chat.id,
                                        message_id=message.message_id-1)
            await message.answer(text="Вибрана дата та час вже минули.",
                                 reply_markup=cancel_notification())
        else:
            time_difference = (target_datetime - current_datetime).total_seconds()
            await bot.edit_message_text(text="Вкажіть час в форматі YYYY-MM-DD hh:mm",
                                        chat_id=message.chat.id,
                                        message_id=message.message_id-1)
            await message.answer(text="Надішліть текст для сповіщення.",
                                 reply_markup=cancel_notification(back=True))
            await state.update_data(datetime=time_difference)
            await state.set_state(States.notification)
    except ValueError:
        await bot.edit_message_text(text="Вкажіть час в форматі YYYY-MM-DD hh:mm",
                                    chat_id=message.chat.id,
                                    message_id=message.message_id-1)
        await message.answer(text="Неправильно введені дані.\n"
                                  "Використовуйте формат YYYY-MM-DD hh:mm\n"
                                  "Спробуйте ще раз",
                             reply_markup=cancel_notification())


@router.message(States.notification)
async def notification(message: types.Message,
                       state: FSMContext,
                       bot: Bot,
                       repo: RequestsRepo) -> None:
    """
    Handler admin input for setting the notification message, scheduling.

    :param message: The message from Telegram.
    :param state: The FSMContext to manage the conversation state.
    :param bot: The bot object used to interact with the Telegram API.
    :param repo: The repository for database requests.
    """
    data = await state.get_data()
    users = await repo.users.get_all_users()
    time = data["datetime"]

    if time is None:
        await send_notification(message=message,
                                bot=bot,
                                data=users)
        await message.answer(text="Сповіщення надіслано")
        await bot.edit_message_text(text="Надішліть текст для сповіщення",
                                    chat_id=message.chat.id,
                                    message_id=message.message_id-1)
        await state.clear()
    else:
        days, remainder = divmod(time, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        scheduler = AsyncIOScheduler()

        job_id = f"{message.date.timestamp()}_{message.from_user.id}"

        scheduler.add_job(func=send_notification,
                          args=(message, bot, users, scheduler),
                          trigger="interval",
                          seconds=time,
                          id=job_id)

        scheduler.start()
        cache[job_id] = scheduler

        await message.answer(text=f"Сповіщення заплановано\n"
                                  f"Відправка через {int(days)} днів, {int(hours)} годин, {int(minutes)} хвилин\n"
                                  f"id: {message.date.timestamp()}_{message.from_user.id}",
                             reply_markup=cancel_scheduler())
        await bot.edit_message_text(text="Надішліть текст для сповіщення",
                                    chat_id=message.chat.id,
                                    message_id=message.message_id-1)
        await bot.pin_chat_message(chat_id=message.chat.id,
                                   message_id=message.message_id+1)

        await state.clear()


@router.callback_query(F.data == "cancel")
async def callback_cancel_scheduler(callback: types.CallbackQuery) -> None:
    """
    Handler the callback from admin who wants to cancel a scheduled notification.

    :param callback: The callback query from the admin.
    """
    job_id = callback.message.text.split("id: ")[-1]
    scheduler = cache.get(job_id)
    scheduler.remove_job(job_id)
    del cache[job_id]
    await callback.message.edit_text(text="Сповіщення скасовано")
    await callback.message.unpin()


@router.callback_query(F.data == "cancel_notification")
async def callback_cancel_notification(callback: types.CallbackQuery,
                                       state: FSMContext) -> None:
    await callback.message.edit_text(text="Сповіщення скасовано")
    await state.clear()


@router.callback_query(F.data == "next")
async def callback_next_notification(callback: types.CallbackQuery,
                                     state: FSMContext) -> None:
    await callback.message.edit_text(text="Надішліть текст для сповіщення.",
                                     reply_markup=cancel_notification(back=True))
    await state.update_data(datetime=None)
    await state.set_state(States.notification)


@router.callback_query(F.data == "back")
async def callback_back_notification(callback: types.CallbackQuery,
                                     state: FSMContext) -> None:
    await callback.message.edit_text(text="Вкажіть час в форматі YYYY-MM-DD hh:mm",
                                     reply_markup=cancel_notification())
    await state.set_state(States.notification_datetime)
