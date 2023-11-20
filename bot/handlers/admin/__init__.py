from typing import List

from aiogram import Router

from bot.filters import Admin
from bot.middlewares import UserIdMiddleware

from . import from_forum, get_db, help, post


def get_admin_routers() -> List[Router]:
    """_summary_

    Returns:
        List[Router]: _description_
    """
    post.router.message.filter(Admin())
    get_db.router.message.filter(Admin())
    help.router.message.filter(Admin())
    from_forum.router.message.filter(Admin(command=False))

    from_forum.router.message.middleware(UserIdMiddleware())
    return [get_db.router, post.router, help.router, from_forum.router]


__all__ = ["get_admin_routers"]
