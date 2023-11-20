import asyncio
import logging
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import Config, load_config
from bot.handlers import get_routers
from bot.middlewares import (
    ConfigMiddleware,
    DatabaseMiddleware,
    MediaGroupMiddleware,
    SchedulerMiddleware,
)
from bot.services import schedule_post
from bot.ui_commands import set_ui_commands


def register_global_middlewares(
    dp: Dispatcher,
    config: Config,
    scheduler: AsyncIOScheduler,
    session_maker: async_sessionmaker,
) -> None:
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_maker),
        SchedulerMiddleware(scheduler),
        MediaGroupMiddleware(),
    ]
    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.ERROR,
        filename="errors.log",
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )


def get_storage(config: Config) -> Union[MemoryStorage, RedisStorage]:
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main() -> None:
    setup_logging()

    config = load_config(path=".env")
    storage = get_storage(config=config)

    engine = create_async_engine(url=config.db.construct_sqlalchemy_url(), echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=schedule_post, args=(bot, session_maker), trigger="cron", hour=12, minute=0
    )

    dp.include_routers(*get_routers())

    register_global_middlewares(
        dp=dp, config=config, scheduler=scheduler, session_maker=session_maker
    )

    await set_ui_commands(bot=bot, config=config)

    try:
        scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        engine.dispose()
        scheduler.shutdown()
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot disabled!")
