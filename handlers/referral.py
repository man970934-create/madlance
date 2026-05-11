"""Реферальная программа"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import db

router = Router()


@router.message(Command("ref"))
@router.message(F.text == "🔗 Реферальная ссылка")
async def referral_link(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала запустите бота через /start")
        return

    link = f"https://t.me/{(await message.bot.get_me()).username}?start=ref{message.from_user.id}"
    await message.answer(
        f"🔗 <b>Ваша реферальная ссылка</b>\n\n"
        f"{link}\n\n"
        f"Приглашайте друзей и получайте +24 часа подписки за каждого!\n"
        f"Количество друзей не ограничено.",
        parse_mode="HTML"
    )
