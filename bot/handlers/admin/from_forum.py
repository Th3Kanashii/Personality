from aiogram import types, Router, Bot

from bot.misc import get_album

router = Router()


@router.message()
async def from_forum(message: types.Message,
                     bot: Bot,
                     user_id: int,
                     album: list[types.Message] = None) -> None:
    """

    :param message:
    :param bot:
    :param user_id:
    :param album:
    """
    if message.media_group_id:
        media = await get_album(album=album)
        await bot.send_media_group(chat_id=user_id,
                                   media=media)

    await message.copy_to(chat_id=user_id)
