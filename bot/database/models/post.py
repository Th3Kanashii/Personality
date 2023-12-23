from sqlalchemy import BIGINT, INTEGER, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("users.user_id"), nullable=False
    )
    post_id: Mapped[str] = mapped_column(String(128))
