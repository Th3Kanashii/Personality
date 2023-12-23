from typing import Final

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from bot.filters import Admin

router: Final[Router] = Router(name=__name__)
router.message.filter(Admin())


@router.message(Command("help"))
async def command_help(message: Message) -> None:
    """
    Handler to /help commands.
    Responds with a help message providing information about available commands.

    :param message: The message from Telegram.
    """
    documentation: FSInputFile = FSInputFile(
        path="data/README.pdf", filename="README.pdf"
    )
    await message.answer_document(
        document=documentation,
        caption="Отримання бази даних у форматі *.xlsx можливе за допомогою команди <b>/db</b>.\n\n"
        "Для проведення масової розсилки повідомлень підписникам використовуйте команду <b>/post</b>, "
        "що забезпечить швидку і зручну взаємодію з аудиторією.\n\n"
        "Уся необхідна інформація, щодо особливостей та можливостей бота, детально описана в файлі <b>README.pdf</b>\n\n"
        "<b>© 2023 Kanashii. Усі права захищено</b>",
    )
