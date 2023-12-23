from typing import Final, List

from aiogram import F, Router

from . import from_user, start, subscription


def get_user_router() -> Router:
    """
    Create and configure a user-specific router.

    :return: A Router object for user interactions.
    """
    user_router: Final[Router] = Router(name=__name__)
    user_router.message.filter(F.chat.type == "private")
    routers_list: List[Router] = [
        start.router,
        subscription.router,
        from_user.router,
    ]
    user_router.include_routers(*routers_list)

    return user_router


__all__: list[str] = [
    "get_user_router",
]
