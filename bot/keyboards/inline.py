from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberMember
from aiogram.utils.keyboard import InlineKeyboardBuilder


def url_subscription(member: ChatMemberMember) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a subscription link.

    :param member: The object ChatMemberMember
    :return: Inline keyboard markup with a button to subscribe.
    """
    if isinstance(member, ChatMemberMember):
        text = "Перейти"
    else:
        text = "Підписатись"
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=text,
                                      url="https://t.me/+Y3QQOvcL7XQxYmU6"))
    return keyboard.as_markup(resize_keyboard=True)


def cancel_scheduler() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a cancel scheduler

    :return: Inline keyboard markup with a button to cancel.
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Скасувати",
                                      callback_data="cancel"))
    return keyboard.as_markup(resize_keyboard=True)


def cancel_notification(back: bool = False) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for next or cancel notification.

    :param back: A boolean flag indicating whether to include the "Назад 🔙" option.
    :return: A ReplyKeyboardMarkup with relevant options.
    """
    keyboard = InlineKeyboardBuilder()
    if back:
        keyboard.row(InlineKeyboardButton(text="Назад 🔙",
                                          callback_data="back"),
                     InlineKeyboardButton(text="Скасувати ❌",
                                          callback_data="cancel_notification"))
    else:
        keyboard.row(InlineKeyboardButton(text="Пропустити ⏭️",
                                          callback_data="next"),
                     InlineKeyboardButton(text="Скасувати ❌",
                                          callback_data="cancel_notification"))

    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)
