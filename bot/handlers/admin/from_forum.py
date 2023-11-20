from aiogram import Bot, Router, html, types

from bot.misc import get_album

router = Router()


@router.message()
async def from_forum(
    message: types.Message,
    bot: Bot,
    user_id: int,
    category: str,
    album: list[types.Message] = None,
) -> None:
    """
    Handler messages from admin and copy them to a user chat.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    :param user_id: The Telegram user ID.
    :param category: The category from admin.
    :param album: List of messages for creating a media album (optional).
    """
    if message.media_group_id:
        media = get_album(
            album=album, category=f"{html.bold(html.italic(html.quote(category)))}"
        )
        await bot.send_media_group(chat_id=user_id, media=media)

    elif message.text:
        await bot.send_message(
            chat_id=user_id,
            text=f"{html.bold(html.italic(html.quote(category)))} {message.text}",
        )

    else:
        await message.copy_to(
            chat_id=user_id,
            caption=f"{html.bold(html.italic(html.quote(category)))}"
            f" {message.caption if message.caption is not None else ''}",
        )
