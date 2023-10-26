import os
import openpyxl

from aiogram import types, Router
from aiogram.filters import Command

from bot.database import RequestsRepo

router = Router()


@router.message(Command(commands=["db"]))
async def get_db(message: types.Message,
                 repo: RequestsRepo) -> None:
    """
    Handler to /db commands.
    Generates a database report in the form of an Excel file and sends it.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    headers = ["ID", "Ім'я", "Прізвище", "Ім'я користувача", "Молодіжна політика", "Психологічна підтримка",
               "Громадянська освіта", "Юридична підтримка"]

    data = await repo.users.get_all_users()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(headers)

    users = 0
    category_counts = [0, 0, 0, 0]

    for row_data in data:
        users += 1
        for i in range(4, 8):
            category_counts[i - 4] += 1 if row_data[i] else 0
        sheet.append(row_data)

    subscription_count = sum(category_counts)
    category_percentages = [round((count / subscription_count) * 100, 1) if subscription_count > 0 else 0 for count in
                            category_counts]

    workbook.save("users.xlsx")
    file_data = types.FSInputFile(path="users.xlsx",
                                  filename="users.xlsx")

    response_text = (
        f"Кількість користувачів у боті - {users}\n"
        f"Кількість підписок - {subscription_count}\n\n"
        f"Молодіжна політика - {category_counts[0]} ({category_percentages[0]}%)\n"
        f"Психологічна підтримка - {category_counts[1]} ({category_percentages[1]}%)\n"
        f"Громадянська освіта - {category_counts[2]} ({category_percentages[2]}%)\n"
        f"Юридична підтримка - {category_counts[3]} ({category_percentages[3]}%)\n"
    )

    await message.answer_document(document=file_data,
                                  caption=response_text)
    os.remove('users.xlsx')
