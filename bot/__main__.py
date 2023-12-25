import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.config import Config, load_config
from bot.handlers import get_routers
from bot.middlewares import ConfigMiddleware, DatabaseMiddleware, SchedulerMiddleware
from bot.services import schedule_post
from bot.ui_commands import set_admin_commands


def register_global_middlewares(
    dp: Dispatcher,
    config: Config,
    scheduler: AsyncIOScheduler,
    session_maker: async_sessionmaker,
) -> None:
    """
    Register global middlewares for the given dispatcher.

    :param dp: The dispatcher instance.
    :param config: The configuration object from the loaded configuration.
    :param scheduler: The asynchronous scheduler for handling scheduled tasks.
    :param session_maker: The session pool object for the database using SQLAlchemy.

    The function registers the following global middlewares for message and callback_query handling:
    1. ConfigMiddleware: Middleware for handling configuration-related operations.
    2. DatabaseMiddleware: Middleware for integrating database operations using SQLAlchemy.
    3. SchedulerMiddleware: Middleware for managing asynchronous scheduled tasks.
    """
    middleware_types: list = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_maker),
        SchedulerMiddleware(scheduler),
    ]
    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging() -> None:
    """
    Set up basic logging configuration.

    This function configures the logging module with the following settings:
    - Logging level is set to ERROR.
    - Log messages are written to a file named "logging.log".
    - Log message format includes filename, line number, log level, timestamp, logger name, and the actual log message.
    """
    logging.basicConfig(
        level=logging.ERROR,
        filename="logging.log",
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )


async def main() -> None:
    setup_logging()

    config: Config = load_config(path=".env")

    engine: AsyncEngine = create_async_engine(
        url=config.db.construct_sqlalchemy_url(), echo=True
    )
    session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, expire_on_commit=False
    )

    bot: Bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())

    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=schedule_post,
        args=(bot, session_maker),
        trigger="cron",
        hour=12,
        minute=0,
        second=0,
    )

    dp.include_routers(*get_routers())

    register_global_middlewares(
        dp=dp, config=config, scheduler=scheduler, session_maker=session_maker
    )

    await set_admin_commands(bot=bot, config=config)

    try:
        scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await engine.dispose()
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
