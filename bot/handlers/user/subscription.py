from aiogram import types, Router, Bot, F

from bot.database import RequestsRepo
from bot.keyboards import cancel_subscription, url_subscription, start

router = Router()


@router.message(F.text.in_(["Молодіжна політика 📚", "Підтримка психолога 🧘", "Громадянська освіта 🏛",
                            "Юридична підтримка ⚖️", "Молодіжна політика ✅", "Підтримка психолога ✅",
                            "Громадянська освіта ✅", "Юридична підтримка ✅"]))
async def subscription(message: types.Message,
                       repo: RequestsRepo) -> None:
    """
    Handler user subscription to specific categories.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    category_mapping = {
        "Молодіжна політика": "Молодіжна політика:  Що приховується за терміном \"молодіжна політика\"? Що означає "
                              "\"молодіжна робота\" у сучасному світі? Хто може стати частиною цієї захоплюючої сфери? "
                              "Які основні відомості та навички потрібні молодіжному працівнику? Як розпочати свій "
                              "власний шлях у цій сфері?",
        "Підтримка психолога": "Ти дізнаєшся:\n\nЯк адаптуватися до нових умов у період війни, як справлятися з "
                               "кризовими та травматичними ситуаціями, що робити з емоційними гойдалками, "
                               "хронічною втомою, стресом, вигорянням, як впоратися з втратою та подолати тривожність "
                               "і страх, що робити коли тебе ніхто не розуміє? Як жити у воєнному та післявоєнному "
                               "суспільстві? Всі ці та свої зпитання ти можеш задати нашому спеціалісту-волонтеру, "
                               "не хвилюйся, запитуй, це анонімно все 😊",
        "Громадянська освіта": "Ти дізнаєшся:\n\nФормування розуміння своїх прав і обов'язків як громадян, а також "
                               "активної участі у суспільстві та демократичному процесі. Ми підготовим тебе до "
                               "ефективної участі в громадянському житті, розвинемо громадянську свідомість, "
                               "толерантність, навчимо  критичного мислення, знання законів державних та людських.",
        "Юридична підтримка": "Ти дізнаєшся:\n\nНадання юридичних консультацій з питань взаємовідносин з державними "
                              "органами та органами місцевого самоврядування;\n\nДопомога в договірній "
                              "роботі;\n\nНадання загальних консультацій з правових питань.\n\nА також маєш можливість "
                              "задати запитання нашому спеціалісту-волонтеру.\n\nНе хвилюйся, запитуй 😊",
    }
    category = category_mapping.get(" ".join(message.text.split()[:-1]))
    await message.answer(text=category,
                         reply_markup=cancel_subscription())
    await repo.users.update_user_subscription(category=message.text,
                                              user_id=message.from_user.id)


@router.message(F.text == "Скасувати підписку ❌")
async def unsubscribe(message: types.Message,
                      repo: RequestsRepo) -> None:
    """
    Handler user cancellation of subscriptions.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    await repo.users.update_user_subscription(user_id=message.from_user.id,
                                              cancel=True)
    subscriptions = await repo.users.get_user_subscriptions(user_id=message.from_user.id)
    await message.answer(text="Підписку скасовано",
                         reply_markup=start(subscriptions))


@router.message(F.text == "Жива бібліотека 📖")
async def living_library_link(message: types.Message,
                              bot: Bot) -> None:
    """
    Handler to provide a link to the live library chat.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    """
    member = await bot.get_chat_member(chat_id="@living_library",
                                       user_id=message.from_user.id)
    await message.answer(text="Жива бібліотека - це місце, де книги оживають завдяки обговоренню і діалозі. Це місце, "
                              "де люди з різних кутків життя збираються, щоб глибше розібратися в літературних "
                              "творах. Кожна книга, представлена в живій бібліотеці, стає виразником авторських ідей, "
                              "тем та символів. Обговорюйте персонажів, діліться враженнями, доносьте послання книг, "
                              "а також власними інтерпретаціями. Насолоджуйтесь!",
                         reply_markup=url_subscription(member=member))


@router.message(F.text == "Головне меню 📌")
async def main_menu(message: types.Message,
                    repo: RequestsRepo) -> None:
    """
    Handler a return to the main menu.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    await repo.users.update_user_subscription(user_id=message.from_user.id,
                                              main_menu=True)
    subscriptions = await repo.users.get_user_subscriptions(user_id=message.from_user.id)
    await message.answer(text="Ви повернулись до головного меню",
                         reply_markup=start(subscriptions))
