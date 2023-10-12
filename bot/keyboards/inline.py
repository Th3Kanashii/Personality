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
                                      url="https://t.me/+tDuRW3cLmqFjNzAy"))
    return keyboard.as_markup(resize_keyboard=True)


def cancel_scheduler() -> InlineKeyboardMarkup:
    """

    :return:
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Скасувати",
                                      callback_data="cancel"))
    return keyboard.as_markup(resize_keyboard=True)
