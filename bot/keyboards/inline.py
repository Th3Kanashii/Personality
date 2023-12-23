from functools import lru_cache
from typing import Literal

from aiogram.types import ChatMemberMember, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@lru_cache
def url_subscription(member: ChatMemberMember) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a subscription link.

    :param member: The object ChatMemberMember
    :return: Inline keyboard markup with a button to subscribe.
    """
    if isinstance(member, ChatMemberMember):
        text: Literal["Перейти"] = "Перейти"
    else:
        text: Literal["Підписатись"] = "Підписатись"
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=text, url="https://t.me/+Y3QQOvcL7XQxYmU6"))
    return keyboard.as_markup(resize_keyboard=True)


def cancel_scheduler() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a cancel scheduler

    :return: Inline keyboard markup with a button to cancel.
    """
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Скасувати", callback_data="cancel"))
    return keyboard.as_markup(resize_keyboard=True)


def cancel_post(back: bool = False) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for next or cancel post.

    :param back: A boolean flag indicating whether to include the "Назад 🔙" option.
    :return: A ReplyKeyboardMarkup with relevant options.
    """
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if back:
        keyboard.row(
            InlineKeyboardButton(text="Назад 🔙", callback_data="back"),
            InlineKeyboardButton(text="Скасувати ❌", callback_data="cancel_post"),
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="Пропустити ⏭️", callback_data="next"),
            InlineKeyboardButton(text="Скасувати ❌", callback_data="cancel_post"),
        )

    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)
