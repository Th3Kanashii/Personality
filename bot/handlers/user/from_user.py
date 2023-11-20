from aiogram import Bot, Router, types

from bot.misc import get_album

router = Router()


@router.message()
async def from_user(
    message: types.Message,
    bot: Bot,
    chat_id: int,
    topic_id: int,
    album: list[types.Message] = None,
) -> None:
    """
    Handler messages from a user and copy them to a specific chat and topic.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param chat_id: The ID of the chat where the message will be copied.
    :param topic_id: The ID of the topic (message thread) where the message will be copied.
    :param album: List of messages for creating a media album (optional).
    """
    if message.media_group_id:
        media = get_album(album=album)
        await bot.send_media_group(
            chat_id=chat_id, media=media, message_thread_id=topic_id
        )
    else:
        await message.copy_to(chat_id=chat_id, message_thread_id=topic_id)
