from .base import BaseRepo
from .posts import PostRepo
from .requests import RequestsRepo
from .users import UserRepo

__all__: list[str] = [
    "BaseRepo",
    "RequestsRepo",
    "UserRepo",
    "PostRepo",
]
