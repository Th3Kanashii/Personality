from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repo.posts import PostRepo
from bot.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def posts(self) -> PostRepo:
        """
        The Post repository sessions are required to manage user operations.
        """
        return PostRepo(self.session)
