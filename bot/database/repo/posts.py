from typing import Optional, Tuple

from sqlalchemy import Select, select
from sqlalchemy.engine.result import Result

from bot.database import Post
from bot.database.repo.base import BaseRepo


class PostRepo(BaseRepo):
    async def add_post(self, user_id: int, post_id: str) -> None:
        """
        Adds a post to the database

        :param user_id: The Telegram user ID.
        :param post_id: The unique ID post.
        """
        post: Post = Post(user_id=user_id, post_id=post_id)
        self.session.add(post)
        await self.session.commit()

    async def get_user_post(self, user_id: int, post_id: str) -> Optional[Post]:
        """
        Check if the user has received post.

        :param user_id: The Telegram user ID.
        :param post_id: The unique ID post.
        :return: The Post object if the record is found, or None if the record is missing.
        """
        query: Select[Tuple[Post]] = select(Post).filter_by(
            user_id=user_id, post_id=post_id
        )
        result: Result[Tuple[Post]] = await self.session.execute(query)
        return result.scalar_one_or_none()
