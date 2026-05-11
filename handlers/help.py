"""FAQ и помощь"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def help_command(message: Message):
    text = (
        "📖 <b>FAQ — Часто задаваемые вопросы</b>\n\n"
        "<b>Как сменить роль/профессию?</b>\n"
        "→ Нажмите /start или кнопку '🔄 Сменить роль'\n\n"
        "<b>Как часто приходят заказы?</b>\n"
        "→ Зависит от активности заказчиков в ваших категориях\n\n"
        "<b>Как пригласить друга?</b>\n"
        "→ Используйте команду /ref\n\n"
        "<b>Как разместить резюме или вакансию?</b>\n"
        "→ Нажмите '💼 Разместить резюме' в меню исполнителя\n\n"
        "<b>Как приобрести подписку?</b>\n"
        "→ Нажмите '💳 Тарифы' в меню исполнителя"
    )
    await message.answer(text, parse_mode="HTML")
