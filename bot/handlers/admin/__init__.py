from aiogram import F

from . import get_db
from . import ban_user
from . import notification
from . import help
from . import from_forum

from bot.middlewares import UserIdMiddleware

get_db.router.message.filter(F.chat.type == "supergroup")
ban_user.router.message.filter(F.chat.type == "supergroup")
notification.router.message.filter(F.chat.type == "supergroup")
help.router.message.filter(F.chat.type == "supergroup")
from_forum.router.message.filter(F.chat.type == "supergroup")

from_forum.router.message.middleware(UserIdMiddleware())

routers_admin = [
    get_db.router,
    ban_user.router,
    notification.router,
    help.router,
    from_forum.router
]

__all__ = [
    "routers_admin"
]
