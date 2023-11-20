from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start(subscriptions: list) -> ReplyKeyboardMarkup:
    """
    Generates a reply keyboard for starting a chat session.

    :param subscriptions: A list of subscription categories.
    :return: A reply keyboard markup with options for each subscription category.
             Subscribed categories are marked with a checkmark (✅).
    """
    keyboard = ReplyKeyboardBuilder()
    categories = [
        "Молодіжна політика 📚",
        "Підтримка психолога 🧘",
        "Громадянська освіта 🏛",
        "Юридична підтримка ⚖️",
        "Жива бібліотека 📖",
    ]
    for category in categories:
        if category in subscriptions:
            keyboard.row(
                KeyboardButton(text=category.replace(category.split()[-1], "✅"))
            )
        else:
            keyboard.row(KeyboardButton(text=category))

    return keyboard.as_markup(resize_keyboard=True)


def cancel_subscription() -> ReplyKeyboardMarkup:
    """
    Generates a reply keyboard for canceling a subscription.

    :return: A reply keyboard markup with options to cancel a subscription and return to the main menu.
    """
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text="Скасувати підписку ❌"),
        KeyboardButton(text="Головне меню 📌"),
    )

    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)
