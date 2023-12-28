from typing import Final, List

from aiogram import F, Router

from .admin import get_admin_routers
from .user import get_user_routers


def get_routers() -> List[Router]:
    """
    Get all routers.

    :return: A list of Router objects for all interactions.
    """
    admin_router: Final[Router] = Router(name=__name__)
    admin_router.message.filter(F.chat.type != "private")
    admin_router.include_routers(*get_admin_routers())

    user_router: Final[Router] = Router(name=__name__)
    user_router.message.filter(F.chat.type == "private")
    user_router.include_routers(*get_user_routers())

    return [
        admin_router,
        user_router,
    ]


__all__: list[str] = [
    "get_routers",
]
