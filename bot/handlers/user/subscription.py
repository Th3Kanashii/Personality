from aiogram import types, Router, Bot, F

from bot.database import DataAccessObject
from bot.keyboards.reply import cancel_subscription, start
from bot.keyboards.inline import url_subscription

router = Router()


@router.message(F.text.in_(["Молодіжна політика 📚", "Підтримка психолога 🧘", "Громадянська освіта 🏛",
                            "Юридична підтримка ⚖️", "Молодіжна політика ✅", "Підтримка психолога ✅",
                            "Громадянська освіта ✅", "Юридична підтримка ✅"]))
async def subscription(message: types.Message,
                       dao: DataAccessObject) -> None:
    """
    Handler user subscription to specific categories.

    :param message: The message from Telegram.
    :param dao: The DataAccessObject for database access.
    """
    category_mapping = {
        "Молодіжна політика": "Ти дізнаєшся:\n\nЩо таке політика. Як живуть політики, яка їхня роль у суспільстві. Як "
                              "розпочати свій шлях з молодіжного крила. Що потрібно знати, як діяти, які складнощі "
                              "чекають на цьому шляху.\n\nА також маєш можливість задати запитання нашому "
                              "спеціалісту-волонтеру.\n\nНе хвилюйся, запитуй 😊",
        "Підтримка психолога": "Ти дізнаєшся:\n\nЯк себе вести на новому місці, локації проживання/навчання, як діяти "
                               "коли ти жертва булінгу, що робити коли тебе ніхто не розуміє, як жити у воєнному та "
                               "післявоєнному суспільстві?\n\nА також маєш можливість задати запитання нашому "
                               "спеціалісту-волонтеру.\n\nНе хвилюйся, запитуй, це анонімно все 😊",
        "Громадянська освіта": "Ти дізнаєшся:\n\nФормування розуміння своїх прав і обов'язків як громадян, а також "
                               "активної участі у суспільстві та демократичному процесі. Ми підготовим тебе до "
                               "ефективної участі в громадянському житті, розвинемо громадянську свідомість, "
                               "толерантність, навчимо  критичного мислення, знання законів державних та людських.",
        "Юридична підтримка": "Ти дізнаєшся:\n\nНадання юридичних консультацій з питань взаємовідносин з державними "
                              "органами та органами місцевого самоврядування;\n\nДопомога в договірній "
                              "роботі;\n\nНадання загальних консультацій з правових питань.\n\nА також маєш можливість "
                              "задати запитання нашому спеціалісту-волонтеру.\n\nНе хвилюйся, запитуй 😊",
    }
    await message.answer(text=category_mapping.get(" ".join(message.text.split()[:-1])),
                         reply_markup=cancel_subscription())
    await dao.update_user_subscription(category=message.text,
                                       user_id=message.from_user.id)


@router.message(F.text == "Скасувати підписку ❌")
async def unsubscribe(message: types.Message,
                      dao: DataAccessObject) -> None:
    """
    Handler user cancellation of subscriptions.

    :param message: The message from Telegram.
    :param dao: The DataAccessObject for database access.
    """
    await dao.update_user_subscription(user_id=message.from_user.id,
                                       cancel=True)
    subscriptions = await dao.get_user_subscriptions(user_id=message.from_user.id)
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
    member = await bot.get_chat_member(chat_id="@living_library", user_id=message.from_user.id)
    await message.answer(text="Ти дізнаєшся:\n\nЖива бібліотека - це інструмент, який намагається боротися з "
                              "упередженнями та дискримінацією. Він працює так само, як звичайна бібліотека: "
                              "відвідувачі можуть переглядати каталог доступних назв, вибрати книгу, яку вони хочуть "
                              "прочитати, і взяти її на обмежений період часу. Після прочитання вони повертають книгу "
                              "в бібліотеку і, якщо хочуть, беруть іншу. Різниця лише в тому, що в Живій Бібліотеці "
                              "книги – це люди, а читання – це розмова.\n\nСпілкуйся, розповідай, давай поради що "
                              "прочитати цікаве та захоплююче!",
                         reply_markup=url_subscription(member=member))


@router.message(F.text == "Головне меню 📌")
async def main_menu(message: types.Message,
                    dao: DataAccessObject) -> None:
    """
    Handler a return to the main menu.

    :param message: The message from Telegram.
    :param dao: The DataAccessObject for database access.
    """
    await dao.update_user_subscription(user_id=message.from_user.id,
                                       main_menu=True)
    subscriptions = await dao.get_user_subscriptions(user_id=message.from_user.id)
    await message.answer(text="Ви повернулись до головного меню",
                         reply_markup=start(subscriptions))
