from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command(commands=["help"]))
async def _help(message: types.Message) -> None:
    await message.answer(text="Команда /db\nПрисилає базу даних у форматі *.xlsx\n\n"
                              "Команда /notification\nРобить сповіщення всім підписникам певної категорії\n"
                              "Якщо виникли якісь труднощі звертайтесь до розробника бота ;)\n\n"
                              "Контакти: @Th3Kanashii, Ім'я: Kanashii\n"
                              "GitHub: https://github.com/Th3Kanashii\n"
                              "Посилання на проєкт:\n"
                              "Ще нема ;(")
