from typing import List

from aiogram import Router

from .admin import get_admin_routers
from .user import get_user_routers


def get_routers() -> List[Router]:
    """

    Returns:
        List[Router]: _description_
    """
    admin_routers: List[Router] = get_admin_routers()
    user_routers: List[Router] = get_user_routers()

    return [*admin_routers, *user_routers]


__all__ = ["get_routers"]
