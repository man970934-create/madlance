"""Админ-панель"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import db
from config import ADMIN_IDS
from keyboards.inline import admin_menu_keyboard

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    await message.answer("🔧 <b>Админ-панель</b>", reply_markup=admin_menu_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.", show_alert=True)
        return
    stats = await db.get_stats()
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👤 Пользователей: {stats['users']}\n"
        f"📝 Заданий: {stats['tasks']}\n"
        f"📄 Резюме: {stats['resumes']}\n"
        f"💎 Подписок: {stats['subscriptions']}\n"
        f"💳 Платежей: {stats['payments']}"
    )
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.", show_alert=True)
        return
    users = await db.get_all_users()
    text = f"👥 <b>Пользователей:</b> {len(users)}\n\n"
    for u in users[:20]:
        role = {"customer": "👔 Заказчик", "executor": "🛠 Исполнитель", "none": "❓ Не выбрал"}.get(u["role"], u["role"])
        text += f"• {u['full_name'] or 'Без имени'} ({u['telegram_id']}) — {role}\n"
    if len(users) > 20:
        text += f"\n... и ещё {len(users) - 20}"
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.", show_alert=True)
        return
    await callback.message.edit_text(
        "📢 <b>Рассылка</b>\n\n"
        "Отправьте сообщение для рассылки всем пользователям.",
        parse_mode="HTML"
    )
    await callback.answer()