from aiogram import types


async def get_album(album: list[types.Message]) -> list:
    """
    Converts a list of messages into a media group for sending as an album.

    :param album: A list of messages to be included in the media group.
    :return: A list of InputMedia objects forming the media group.
    """
    media_group = []
    for msg in album:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            media_group.append(types.InputMediaPhoto(media=file_id,
                                                     caption=msg.caption))
        else:
            obj_dict = msg.dict()
            file_id = obj_dict[msg.content_type]['file_id']
            media_group.append(types.InputMedia(media=file_id))
    return media_group
