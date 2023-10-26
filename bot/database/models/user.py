from typing import Optional

from sqlalchemy import String, BIGINT, BOOLEAN, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[Optional[str]] = mapped_column(String(128))
    username: Mapped[Optional[str]] = mapped_column(String(128))
    youth_policy: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    psychologist_support: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    civic_education: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    legal_support: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    youth_policy_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    psychologist_support_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    legal_support_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    active_category: Mapped[Optional[str]] = mapped_column(String(128))
