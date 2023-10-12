from aiogram import F

from . import start
from . import subscription
from . import from_user

from bot.middlewares import RegisterUserMiddleware, TopicMiddleware, ThrottlingMiddleware

start.router.message.filter(F.chat.type == "private")
subscription.router.message.filter(F.chat.type == "private")
from_user.router.message.filter(F.chat.type == "private")

start.router.message.middleware(RegisterUserMiddleware())
start.router.message.middleware(ThrottlingMiddleware(limit=15))
from_user.router.message.middleware(ThrottlingMiddleware())
from_user.router.message.middleware(TopicMiddleware())

routers_user = [
    start.router,
    subscription.router,
    from_user.router
]

__all__ = [
    "routers_user"
]
