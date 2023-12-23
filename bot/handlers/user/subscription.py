from typing import Dict, Final, List

from aiogram import Bot, F, Router
from aiogram.types import ChatMemberMember, Message

from bot.database import RequestsRepo
from bot.keyboards import cancel_subscription, start, url_subscription

router: Final[Router] = Router(name=__name__)

categories_subscribe: Final[List[str]] = [
    "Молодіжна політика 📚",
    "Підтримка психолога 🧘",
    "Громадянська освіта 🏛",
    "Юридична підтримка ⚖️",
]
categories_subscribed: Final[List[str]] = [
    "Молодіжна політика ✅",
    "Підтримка психолога ✅",
    "Юридична підтримка ✅",
    "Громадянська освіта ✅",
]


@router.message(F.text.in_(categories_subscribe))
async def subscribe(message: Message, repo: RequestsRepo) -> None:
    """
    Handler user subscription to specific categories.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    category_mapping: Dict[str, str] = {
        "Молодіжна політика": (
            'Молодіжна політика: Що приховується за терміном "молодіжна політика"? Що означає '
            '"молодіжна робота" у сучасному світі? Хто може стати частиною цієї захоплюючої сфери? '
            "Які основні відомості та навички потрібні молодіжному працівнику? Як розпочати свій "
            "власний шлях у цій сфері?"
        ),
        "Підтримка психолога": (
            "Ти дізнаєшся:\n\nЯк адаптуватися до нових умов у період війни, як справлятися з "
            "кризовими та травматичними ситуаціями, що робити з емоційними гойдалками, "
            "хронічною втомою, стресом, вигорянням, як впоратися з втратою та подолати тривожність "
            "і страх, що робити коли тебе ніхто не розуміє? Як жити у воєнному та післявоєнному "
            "суспільстві? Всі ці та свої запитання ти можеш задати нашому спеціалісту-волонтеру, "
            "не хвилюйся, запитуй, це анонімно все 😊"
        ),
        "Громадянська освіта": (
            "Ти дізнаєшся:\n\nФормування розуміння своїх прав і обов'язків як громадян, а також "
            "активної участі у суспільстві та демократичному процесі. Ми підготовим тебе до "
            "ефективної участі в громадянському житті, розвинемо громадянську свідомість, "
            "толерантність, навчимо критичного мислення, знання законів державних та людських."
        ),
        "Юридична підтримка": (
            "Ти дізнаєшся:\n\nНадання юридичних консультацій з питань взаємовідносин з державними "
            "органами та органами місцевого самоврядування;\n\nДопомога в договірній "
            "роботі;\n\nНадання загальних консультацій з правових питань.\n\nА також маєш можливість "
            "задати запитання нашому спеціалісту-волонтеру.\n\nНе хвилюйся, запитуй 😊"
        ),
    }

    category: str = category_mapping.get(" ".join(message.text.split()[:-1]))
    await message.answer(text=category, reply_markup=cancel_subscription())
    await repo.users.update_user_subscription(
        category=message.text, user_id=message.from_user.id
    )


@router.message(F.text.in_(categories_subscribed))
async def subscribed(message: Message, repo: RequestsRepo) -> None:
    """
    Handler user subscribed.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    if message.text == "Громадянська освіта ✅":
        await message.answer(
            text="Спілкування з волонтером не доступно",
            reply_markup=cancel_subscription(),
        )
    else:
        await message.answer(
            text="Слова твої - вогінь, пиши мені, шаленій! 🤗",
            reply_markup=cancel_subscription(),
        )
    await repo.users.update_user_subscription(
        category=message.text, user_id=message.from_user.id
    )


@router.message(F.text == "Скасувати підписку ❌")
async def unsubscribe(message: Message, repo: RequestsRepo) -> None:
    """
    Handler user cancellation of subscriptions.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    await repo.users.update_user_subscription(user_id=message.from_user.id, cancel=True)
    subscriptions: List[str] = await repo.users.get_user_subscriptions(
        user_id=message.from_user.id
    )
    await message.answer(text="Підписку скасовано", reply_markup=start(subscriptions))


@router.message(F.text == "Жива бібліотека 📖")
async def living_library_link(message: Message, bot: Bot) -> None:
    """
    Handler to provide a link to the live library chat.

    :param message: The message from Telegram.
    :param bot: The bot object used to interact with the Telegram API.
    """
    member: ChatMemberMember = await bot.get_chat_member(
        chat_id="@living_library", user_id=message.from_user.id
    )
    await message.answer(
        text="Жива бібліотека - це місце, де книги оживають завдяки обговоренню і діалозі. Це місце, "
        "де люди з різних кутків життя збираються, щоб глибше розібратися в літературних "
        "творах. Кожна книга, представлена в живій бібліотеці, стає виразником авторських ідей, "
        "тем та символів. Обговорюйте персонажів, діліться враженнями, доносьте послання книг, "
        "а також власними інтерпретаціями. Насолоджуйтесь!",
        reply_markup=url_subscription(member=member),
    )


@router.message(F.text == "Головне меню 📌")
async def main_menu(message: Message, repo: RequestsRepo) -> None:
    """
    Handler a return to the main menu.

    :param message: The message from Telegram.
    :param repo: The repository for database requests.
    """
    await repo.users.update_user_subscription(
        user_id=message.from_user.id, main_menu=True
    )
    subscriptions: List[str] = await repo.users.get_user_subscriptions(
        user_id=message.from_user.id
    )
    await message.answer(
        text="Ви повернулись до головного меню", reply_markup=start(subscriptions)
    )
