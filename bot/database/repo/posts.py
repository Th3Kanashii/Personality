from typing import Optional

from sqlalchemy import select

from bot.database import Post
from bot.database.repo.base import BaseRepo


class PostRepo(BaseRepo):
    async def add_post(self, user_id: int, post_id: str) -> None:
        """ """
        post = Post(user_id=user_id, post_id=post_id)
        self.session.add(post)
        await self.session.commit()

    async def get_user_post(self, user_id: int, post_id: str) -> Optional[Post]:
        query = select(Post).filter_by(user_id=user_id, post_id=post_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
