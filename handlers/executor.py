"""Логика исполнителя"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.inline import categories_keyboard, tariffs_keyboard
from keyboards.reply import main_executor_keyboard
from utils.states import ExecutorFlow

router = Router()


@router.message(F.text == "📂 Мои категории")
async def my_categories(message: Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user or user["role"] != "executor":
        await message.answer("Сначала выберите роль Исполнителя через /start")
        return

    await message.answer(
        "Выберите интересующие категории (можно несколько):",
        reply_markup=categories_keyboard(multi=True)
    )
    await state.set_state(ExecutorFlow.choosing_categories)
    await state.update_data(selected_cats=[])


@router.callback_query(ExecutorFlow.choosing_categories, F.data.startswith("cat:"))
async def process_executor_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_cats", [])
    cat_name = callback.data.split(":", 1)[1]

    if cat_name == "done":
        user = await db.get_user_by_telegram_id(callback.from_user.id)
        cats = await db.get_categories()
        cat_map = {c["name"]: c["id"] for c in cats}
        selected_ids = [cat_map[c] for c in selected if c in cat_map]
        await db.set_user_categories(user["id"], selected_ids)
        await callback.message.edit_text(
            f"✅ Категории сохранены: {', '.join(selected) if selected else 'Не выбрано'}"
        )
        await state.clear()
        await callback.answer()
        return

    if cat_name in selected:
        selected.remove(cat_name)
    else:
        selected.append(cat_name)

    await state.update_data(selected_cats=selected)
    await callback.message.edit_reply_markup(reply_markup=categories_keyboard(selected=selected, multi=True))
    await callback.answer()


@router.callback_query(F.data.startswith("task_accept:"))
async def accept_task(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    task = await db.get_task(task_id)
    if not task:
        await callback.answer("Задание не найдено.", show_alert=True)
        return

    customer = await db.get_user_by_id(task["user_id"])
    contact = f"@{customer['username']}" if customer.get("username") else f"ID: {customer['telegram_id']}"

    await callback.message.edit_text(
        f"✅ Вы приняли задание!\n\n"
        f"<b>{task['title']}</b>\n"
        f"{task['description']}\n\n"
        f"📞 Контакт заказчика: {contact}",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_reject:"))
async def reject_task(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Задание отклонено.")


@router.message(F.text == "💳 Тарифы")
async def show_tariffs(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    sub = await db.get_active_subscription(user["id"]) if user else None

    text = "📋 <b>Тарифы подписки</b>\n\n"
    if sub:
        from datetime import datetime
        end = sub["end_date"]
        text += f"✅ Активна подписка до: {end[:10]}\n\n"

    text += (
        "🗓 Неделя — 200 ₽\n"
        "🗓 Месяц — 600 ₽\n"
        "🗓 3 месяца — 1400 ₽\n\n"
        "Выберите тариф:"
    )
    await message.answer(text, reply_markup=tariffs_keyboard(), parse_mode="HTML")
