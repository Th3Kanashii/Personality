from aiogram import types, Router, Bot

from bot.misc import get_album

router = Router()


@router.message()
async def from_forum(message: types.Message,
                     bot: Bot,
                     user_id: int,
                     album: list[types.Message] = None) -> None:
    """
    Handler messages from admin and copy them to a user chat.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param user_id: The Telegram user ID.
    :param album: List of messages for creating a media album (optional).
    """
    if message.media_group_id:
        media = await get_album(album=album)
        await bot.send_media_group(chat_id=user_id,
                                   media=media)
        return

    await message.copy_to(chat_id=user_id)
