from typing import List

from aiogram import Router

from bot.filters import Admin
from bot.middlewares import AlbumMiddleware, UserIdMiddleware

from . import all, from_forum, get_db, help, post


def get_admin_routers() -> List[Router]:
    """
    Get a list of routers with admin filters and specific middlewares.

    :return: A list of routers with admin filters and middleware applied.
    """
    all.router.message.filter(Admin())
    get_db.router.message.filter(Admin())
    post.router.message.filter(Admin())
    help.router.message.filter(Admin())
    from_forum.router.message.filter(Admin(command=False))

    from_forum.router.message.middleware(AlbumMiddleware())
    from_forum.router.message.middleware(UserIdMiddleware())

    routers_list: List[Router] = [
        all.router,
        get_db.router,
        post.router,
        help.router,
        from_forum.router,
    ]

    return routers_list


__all__: list[str] = [
    "get_admin_routers",
]
