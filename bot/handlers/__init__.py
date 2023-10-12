from aiogram import Router

from .admin import routers_admin
from .user import routers_user


def get_router() -> Router:
    main_router = Router()
    routers = routers_user + routers_admin
    for router in routers:
        main_router.include_router(router)

    return main_router


__all__ = [
    "get_router"
]
