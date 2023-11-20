from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.config import Config


async def set_ui_commands(bot: Bot, config: Config) -> None:
    """_summary_

    :param bot: _description_
    :type bot: Bot
    """
    for chat_id in config.tg_bot.all_groups:
        await bot.set_my_commands(
            commands=[
                BotCommand(command="help", description="Допомога"),
                BotCommand(command="post", description="Розсилка"),
                BotCommand(command="db", description="База даних"),
            ],
            scope=BotCommandScopeChat(chat_id=chat_id),
        )
