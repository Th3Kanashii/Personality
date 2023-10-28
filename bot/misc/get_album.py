from aiogram import types


async def get_album(album: list[types.Message],
                    category: str = None) -> list:
    """
    Converts a list of messages into a media group for sending as an album.

    :param album: A list of messages to be included in the media group.
    :param category: An optional category to add to the captions.
    :return: A list of InputMedia objects forming the media group.
    """
    media_group = []

    for msg in album:
        caption = f"{category} {msg.caption or ''}" if category is not None else msg.caption

        if msg.photo:
            media_type = types.InputMediaPhoto
            media = msg.photo[-1].file_id
        elif msg.document:
            media_type = types.InputMediaDocument
            media = msg.document.file_id
        elif msg.audio:
            media_type = types.InputMediaAudio
            media = msg.audio.file_id
        elif msg.video:
            media_type = types.InputMediaVideo
            media = msg.video.file_id
        else:
            media_type = types.InputMediaAnimation
            media = msg.animation.file_id

        if msg == album[0]:
            media_group.append(media_type(media=media, caption=caption))
        else:
            media_group.append(media_type(media=media))

    return media_group
