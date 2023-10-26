from . import get_db
from . import notification
from . import help
from . import from_forum

from bot.config import load_config
from bot.filters import Admin
from bot.middlewares import UserIdMiddleware

config = load_config()
admins = config.tg_bot.admins

get_db.router.message.filter(Admin(admins=admins))
notification.router.message.filter(Admin(admins=admins))
help.router.message.filter(Admin(admins=admins))
from_forum.router.message.filter(Admin(admins=admins, command=False))

from_forum.router.message.middleware(UserIdMiddleware())

routers_admin = [
    get_db.router,
    notification.router,
    help.router,
    from_forum.router
]

__all__ = [
    "routers_admin"
]
