import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Union

from aiogram import BaseMiddleware, html
from aiogram.types import CallbackQuery, InputMedia, InputMediaPhoto, Message


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        self.latency = latency

    @staticmethod
    def get_album(album: List[Message], category: str) -> List[InputMedia]:
        """
        Creates a list of media elements suitable for creating an album.

        :param album: A list of Message objects representing the album content.
        :param category: A category string for captions.
        :return: List of InputMedia objects for constructing a media album.
        """
        media_group: list = []
        for message in album:
            caption = (
                f"{category} {message.caption or ''}"
                if category is not None
                else message.caption
            )
            if message.photo:
                file_id: str = message.photo[-1].file_id
                media_group.append(InputMediaPhoto(media=file_id, caption=caption))
            else:
                obj_dict: Dict[str, Any] = message.model_dump()
                file_id: str = obj_dict[message.content_type]["file_id"]
                media_group.append(InputMedia(media=file_id, caption=caption))

        return media_group

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            await handler(event, data)
            return
        try:
            self.album_data[event.media_group_id].append(event)
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)

            data["_is_last"] = True
            data["album"] = self.get_album(
                album=self.album_data[event.media_group_id],
                category=f"{html.bold(html.italic(event.chat.title.split('/')[1]))}: {event.caption}",
            )
            await handler(event, data)

        if event.media_group_id and data.get("_is_last"):
            del self.album_data[event.media_group_id]
            del data["_is_last"]
