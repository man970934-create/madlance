"""Inline клавиатуры"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CATEGORIES, TARIFFS


def role_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👔 Я Заказчик", callback_data="role:customer")],
        [InlineKeyboardButton(text="🛠 Я Исполнитель", callback_data="role:executor")],
    ])


def change_role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Перевыбрать роль", callback_data="role:change")]
    ])


def categories_keyboard(selected: list = None, multi: bool = False) -> InlineKeyboardMarkup:
    selected = selected or []
    buttons = []
    for cat in CATEGORIES:
        prefix = "✅ " if cat in selected else ""
        buttons.append([InlineKeyboardButton(text=f"{prefix}{cat}", callback_data=f"cat:{cat}")])
    if multi:
        buttons.append([InlineKeyboardButton(text="✅ Готово", callback_data="cat:done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_task_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать за 100 ₽", callback_data="task:confirm")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="task:edit")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="task:cancel")],
    ])


def task_action_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"task_accept:{task_id}")],
        [InlineKeyboardButton(text="❌ Отказать", callback_data=f"task_reject:{task_id}")],
    ])


def tariffs_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, t in TARIFFS.items():
        buttons.append([InlineKeyboardButton(text=t["label"], callback_data=f"tariff:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_method_keyboard(payment_type: str = "") -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💎 CryptoBot (Криптовалюта)",
            callback_data=f"pay_crypto:{payment_type}"
        )],
        [InlineKeyboardButton(
            text="💳 ЮKassa (Банковская карта)",
            callback_data=f"pay_yookassa:{payment_type}"
        )],
        [InlineKeyboardButton(text="« Назад", callback_data="show_tariffs")]
    ])


def confirm_resume_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать за 100 ₽", callback_data="resume:confirm")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="resume:edit")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="resume:cancel")],
    ])


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast")],
        [InlineKeyboardButton(text="📋 Задания", callback_data="admin:tasks")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users")],
    ])
