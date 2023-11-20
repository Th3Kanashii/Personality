from typing import List

from aiogram import Router

from bot.filters import User
from bot.middlewares import (
    RegisterUserMiddleware,
    ThrottlingMiddleware,
    TopicMiddleware,
)

from . import from_user, start, subscription


def get_user_routers() -> List[Router]:
    """_summary_

    Returns:
        List[Router]: _description_
    """
    start.router.message.filter(User())
    subscription.router.message.filter(User())
    from_user.router.message.filter(User())

    start.router.message.middleware(RegisterUserMiddleware())
    start.router.message.middleware(ThrottlingMiddleware(limit=5))
    from_user.router.message.middleware(ThrottlingMiddleware())
    from_user.router.message.middleware(TopicMiddleware())

    return [start.router, subscription.router, from_user.router]


__all__ = ["get_user_routers"]
