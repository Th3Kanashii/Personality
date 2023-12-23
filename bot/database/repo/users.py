from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import Select, select
from sqlalchemy.engine.result import Result

from bot.database import User
from bot.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user from the database by their ID.

        :param user_id: The Telegram user ID.
        :return: User object or None if the user is not found.
        """
        return await self.session.get(User, user_id)

    async def add_user(
        self, user_id: int, first_name: str, last_name: str, username: str
    ) -> None:
        """
        Adds a user to the database or updates an existing user.

        :param user_id: The Telegram user ID.
        :param first_name: The Telegram user first_name.
        :param last_name: The Telegram user last_name.
        :param username: The Telegram user username.
        """
        user: User = User(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        self.session.add(user)
        await self.session.commit()

    async def update_user_subscription(
        self,
        user_id: int,
        cancel: bool = False,
        main_menu: bool = False,
        category: Optional[str] = None,
    ) -> None:
        """
        Renews or cancels a user's subscription to a category.

        :param user_id: The Telegram user ID.
        :param category: The category that the user wants to update.
        :param cancel: If True, unsubscribe from the specified category.
        :param main_menu: If True, update active category is None
        """
        category_mapping: Dict[str, str] = {
            "Молодіжна політика": "youth_policy",
            "Підтримка психолога": "psychologist_support",
            "Громадянська освіта": "civic_education",
            "Юридична підтримка": "legal_support",
        }
        user: Union[User, None] = await self.get_user(user_id)

        if cancel:
            setattr(user, user.active_category, False)
            user.active_category = None
        elif main_menu:
            user.active_category = None
        else:
            key = category_mapping.get(" ".join(category.split()[:-1]))
            setattr(user, key, True)
            user.active_category = key

        await self.session.commit()

    async def get_user_subscriptions(self, user_id: int) -> List[str]:
        """
        Gets a list of user subscriptions.

        :param user_id: The Telegram user ID.
        :return: List of user subscriptions.
        """
        categories: Dict[str, str] = {
            "youth_policy": "Молодіжна політика 📚",
            "psychologist_support": "Підтримка психолога 🧘",
            "civic_education": "Громадянська освіта 🏛",
            "legal_support": "Юридична підтримка ⚖️",
        }
        user: Union[User, None] = await self.get_user(user_id)
        subscriptions: List[str] = [
            categories[category] for category in categories if getattr(user, category)
        ]
        return subscriptions

    async def add_topic_id(self, user_id: int, topic_id: int) -> None:
        """
        Add topic id in database

        :param user_id: The Telegram user ID.
        :param topic_id: The ID of the topic related to the user.
        """
        user: Union[User, None] = await self.get_user(user_id=user_id)
        setattr(user, f"{user.active_category}_topic", topic_id)
        await self.session.commit()

    async def get_user_id_by_topic(self, topic_id: int, category: str) -> int:
        """
        Retrieve a user ID based on a specific topic ID and category.

        :param topic_id: The ID of the topic to search for.
        :param category: The category to search within.
        :return: The user ID associated with the provided topic and category.
        """
        query: Select[Tuple[int]] = select(User.user_id).where(
            getattr(User, f"{category}_topic") == topic_id
        )
        return await self.session.scalar(query)

    async def get_all_users(self) -> List[tuple]:
        """
        Retrieve a list of all users in the database.

        :return: A list of tuples containing user data.
        """
        fields: Tuple[str, ...] = (
            "user_id",
            "first_name",
            "last_name",
            "username",
            "youth_policy",
            "psychologist_support",
            "civic_education",
            "legal_support",
        )

        users: Result[Tuple[User]] = await self.session.execute(select(User))
        user_data: List[Tuple] = [
            tuple(getattr(user, field) for field in fields) for user in users.scalars()
        ]

        return user_data
