from typing import List

from aiogram import Router

from bot.middlewares import (
    AlbumMiddleware,
    RegisterUserMiddleware,
    ThrottlingMiddleware,
    TopicMiddleware,
)

from . import from_user, start, subscription


def get_user_routers() -> List[Router]:
    """
    Get a list of routers with user filters and specific middlewares.

    :return: A list of routers with user filters and middleware applied.
    """
    start.router.message.middleware(RegisterUserMiddleware())
    start.router.message.middleware(ThrottlingMiddleware(limit=3))
    from_user.router.message.middleware(AlbumMiddleware())
    from_user.router.message.middleware(ThrottlingMiddleware())
    from_user.router.message.middleware(TopicMiddleware())

    routers_list: List[Router] = [
        start.router,
        subscription.router,
        from_user.router,
    ]

    return routers_list


__all__: list[str] = [
    "get_user_routers",
]
