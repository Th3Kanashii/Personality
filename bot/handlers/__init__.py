from typing import List

from aiogram import Router

from .admin import get_admin_router
from .user import get_user_router


def get_routers() -> List[Router]:
    """
    Get all routers.

    :return: A list of Router objects for all interactions.
    """
    admin_router: Router = get_admin_router()
    user_router: Router = get_user_router()

    return [
        admin_router,
        user_router,
    ]


__all__: list[str] = ["get_routers"]
