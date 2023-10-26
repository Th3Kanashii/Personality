from . import start
from . import subscription
from . import from_user

from bot.filters import User
from bot.middlewares import RegisterUserMiddleware, TopicMiddleware, ThrottlingMiddleware

start.router.message.filter(User())
subscription.router.message.filter(User())
from_user.router.message.filter(User())

start.router.message.middleware(RegisterUserMiddleware())
start.router.message.middleware(ThrottlingMiddleware(limit=5))
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
