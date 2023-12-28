import csv
import os
from typing import Final, List, Literal, Union

import aiofiles
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from bot.database import RequestsRepo

router: Final[Router] = Router(name=__name__)


@router.message(Command("db"))
async def get_db(message: Message, repo: RequestsRepo) -> None:
    """
    Handler to /db commands.
    Generates a database report in the form of an Excel file and sends it.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    headers: List[str] = [
        "ID",
        "Ім'я",
        "Прізвище",
        "Ім'я користувача",
        "Молодіжна політика",
        "Психологічна підтримка",
        "Громадянська освіта",
        "Юридична підтримка",
    ]

    data: List[tuple] = await repo.users.get_all_users()

    users: Literal[0] = 0
    category_counts: List[int] = [0, 0, 0, 0]

    async with aiofiles.open(
        "users.csv", mode="w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        await writer.writerow(headers)

        for row_data in data:
            users += 1
            for i in range(4, 8):
                category_counts[i - 4] += 1 if row_data[i] else 0
            await writer.writerow(row_data)

    subscription_count: int = sum(category_counts)
    category_percentages: List[Union[float, int]] = [
        round((count / subscription_count) * 100, 1) if subscription_count > 0 else 0
        for count in category_counts
    ]
    file_data: FSInputFile = FSInputFile(path="users.csv", filename="users.csv")

    response_text: str = (
        f"Кількість користувачів у боті - {users}\n"
        f"Кількість підписок - {subscription_count}\n\n"
        f"Молодіжна політика - {category_counts[0]} ({category_percentages[0]}%)\n"
        f"Психологічна підтримка - {category_counts[1]} ({category_percentages[1]}%)\n"
        f"Громадянська освіта - {category_counts[2]} ({category_percentages[2]}%)\n"
        f"Юридична підтримка - {category_counts[3]} ({category_percentages[3]}%)\n"
    )

    await message.answer_document(document=file_data, caption=response_text)

    os.remove("users.csv")
