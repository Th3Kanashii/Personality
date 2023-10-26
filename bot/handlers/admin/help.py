from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command(commands=["help"]))
async def command_help(message: types.Message) -> None:
    """
    Handler to /help commands.
    Responds with a help message providing information about available commands.

    :param message: The message from Telegram.
    """
    await message.answer(text="Команда /db\nПрисилає базу даних у форматі *.xlsx\n\n"
                              "Команда /notification\nРобить сповіщення всім підписникам\n"
                              "Якщо виникли якісь труднощі, звертайтесь до розробника ;)\n\n"
                              "Контакти: @Th3Kanashii, Ім'я: Kanashii\n"
                              "GitHub: https://github.com/Th3Kanashii\n"
                              "Посилання на проєкт:\n"
                              "https://github.com/Th3Kanashii/Personality.git")
