import logging
import sys
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import load_config
from bot.misc import schedule_notification
from bot.handlers import get_router
from bot.middlewares import DatabaseMiddleware, ConfigMiddleware, MediaGroupMiddleware


async def main() -> None:
    config = load_config(path=".env")
    engine = create_async_engine(url=config.db.construct_sqlalchemy_url(), echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    dp.message.outer_middleware(DatabaseMiddleware(session_maker))
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.message.outer_middleware(MediaGroupMiddleware())

    main_router = get_router()
    dp.include_router(main_router)

    scheduler.add_job(func=schedule_notification,
                      args=(bot, session_maker),
                      trigger="cron",
                      hour=12,
                      minute=0)

    scheduler.start()

    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
