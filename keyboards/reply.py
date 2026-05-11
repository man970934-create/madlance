"""Reply клавиатуры"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_customer_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Создать задание")],
            [KeyboardButton(text="📋 Мои задания"), KeyboardButton(text="💳 Баланс")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔄 Сменить роль")],
        ],
        resize_keyboard=True
    )


def main_executor_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Мои категории")],
            [KeyboardButton(text="💼 Разместить резюме"), KeyboardButton(text="💳 Тарифы")],
            [KeyboardButton(text="🔗 Реферальная ссылка"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="🔄 Сменить роль")],
        ],
        resize_keyboard=True
    )


def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏭ Пропустить")]],
        resize_keyboard=True
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True
    )
