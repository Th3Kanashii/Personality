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
    documentation = types.FSInputFile(path="README.pdf", filename="README.pdf")
    await message.answer_document(
        document=documentation,
        caption="Отримання бази даних у форматі *.xlsx можливе за допомогою команди <b>/db</b>.\n\n"
        "Для проведення масової розсилки повідомлень підписникам використовуйте команду <b>/post</b>, "
        "що забезпечить швидку і зручну взаємодію з аудиторією.\n\n"
        "Уся необхідна інформація, щодо особливостей та можливостей бота, детально описана в файлі <b>README.pdf</b>\n\n"
        "<b>© 2023 Kanashii. Усі права захищено</b>",
    )
