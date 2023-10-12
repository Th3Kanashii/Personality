from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import LRUCache
from datetime import datetime

from bot.database import DataAccessObject
from bot.keyboards import cancel_notification, cancel_scheduler
from bot.misc import States, send_notification, get_album

router = Router()
cache = LRUCache(maxsize=5)


@router.message(Command(commands=["notification"]))
async def command_notification(message: types.Message,
                               state: FSMContext) -> None:
    await message.answer(text="Вкажіть час в форматі hh.mm",
                         reply_markup=cancel_notification())
    await state.set_state(States.notification_time)


@router.message(States.notification_time)
async def time_notification(message: types.Message,
                            state: FSMContext) -> None:
    if message.text == "Скасувати ❌":
        await message.answer(text="Сповіщення скасовано",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    elif message.text == "Пропустити ⏭️":
        await message.answer(text="Надішліть текст для сповіщення",
                             reply_markup=cancel_notification(back=True))
        await state.update_data(time=0)
        await state.set_state(States.notification)
    else:
        try:
            hours, minutes = map(int, message.text.split("."))
            interval_seconds = (hours * 3600) + (minutes * 60)
            await message.answer(text="Надішліть текст для сповіщення",
                                 reply_markup=cancel_notification(back=True))
            await state.update_data(time=interval_seconds)
            await state.set_state(States.notification)
        except ValueError:
            await message.answer(text="Неправильно введено час",
                                 reply_markup=cancel_notification())


@router.message(States.notification)
async def notification(message: types.Message,
                       bot: Bot,
                       state: FSMContext,
                       dao: DataAccessObject,
                       album: list[types.Message] = None) -> None:
    media = None
    data = await state.get_data()
    users = await dao.get_all_users()
    time = data["time"]

    if message.media_group_id:
        media = await get_album(album)

    if message.text == "Назад 🔙":
        await message.answer(text="Вкажіть час в форматі hh.mm",
                             reply_markup=cancel_notification())
        await state.set_state(States.notification_time)
    elif message.text == "Скасувати ❌":
        await message.answer(text="Сповіщення скасовано",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    elif time == 0:
        await send_notification(message=message,
                                bot=bot,
                                data=users,
                                media=media)
        await message.answer(text="Сповіщення надіслано",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    else:
        current_time = datetime.now().time()
        current_hour, current_minute = current_time.hour, current_time.minute
        time_difference_seconds = time - (current_hour * 60 + current_minute) * 60

        scheduler = AsyncIOScheduler()

        job_id = f"{message.date.timestamp()}_{message.from_user.id}"

        scheduler.add_job(func=send_notification,
                          args=(message, bot, users, scheduler, media),
                          trigger='interval',
                          seconds=time_difference_seconds,
                          id=job_id)

        scheduler.start()
        cache[job_id] = scheduler

        await message.answer(text="Сповіщення заплановано",
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer(text=f"Відправка через {time_difference_seconds // 60} хвилин(у)\n"
                                  f"id: {message.date.timestamp()}_{message.from_user.id}",
                             reply_markup=cancel_scheduler())

        await state.clear()


@router.callback_query(F.data == "cancel")
async def _cancel_scheduler(callback: types.CallbackQuery):
    job_id = callback.message.text.split("id: ")[-1]
    scheduler = cache.get(job_id)
    scheduler.remove_job(job_id)
    del cache[job_id]
    await callback.message.edit_text(text="Скасовано")
