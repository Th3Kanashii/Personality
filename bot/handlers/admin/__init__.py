from typing import Final, List

from aiogram import F, Router

from . import all, from_forum, get_db, help, post


def get_admin_router() -> Router:
    """
    Create and configure a admin-specific router.

    :return: A Router object for admin interactions.
    """
    admin_router: Final[Router] = Router(name=__name__)
    admin_router.message.filter(F.chat.type != "private")
    routers_list: List[Router] = [
        all.router,
        get_db.router,
        post.router,
        help.router,
        from_forum.router,
    ]
    admin_router.include_routers(*routers_list)

    return admin_router


__all__: list[str] = [
    "get_admin_router",
]
