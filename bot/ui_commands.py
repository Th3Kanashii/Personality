from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.config import Config


async def set_admin_commands(bot: Bot, config: Config) -> None:
    """
    Set custom admin interface commands for each group chat based on the provided configuration.

    :param bot: The bot object used to interact with the Telegram API.
    :param config: The configuration object containing information about all group chats.
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
