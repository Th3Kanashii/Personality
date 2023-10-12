from typing import Optional

from sqlalchemy import String, BIGINT, Boolean, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[Optional[str]] = mapped_column(String(128))
    username: Mapped[Optional[str]] = mapped_column(String(128))
    youth_policy: Mapped[bool] = mapped_column(Boolean, default=False)
    psychologist_support: Mapped[bool] = mapped_column(Boolean, default=False)
    civic_education: Mapped[bool] = mapped_column(Boolean, default=False)
    legal_support: Mapped[bool] = mapped_column(Boolean, default=False)
    youth_policy_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    psychologist_support_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    civic_education_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    legal_support_topic: Mapped[Optional[int]] = mapped_column(INTEGER)
    ban: Mapped[bool] = mapped_column(Boolean, default=False)
    active_category: Mapped[Optional[str]] = mapped_column(String(128))
