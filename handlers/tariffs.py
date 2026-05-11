"""Тарифы и оплата подписок"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext

from database import db
from config import TARIFFS
from keyboards.inline import country_choice_keyboard
from keyboards.reply import main_executor_keyboard

router = Router()


@router.callback_query(F.data.startswith("tariff:"))
async def process_tariff(callback: CallbackQuery, bot: Bot):
    tariff_key = callback.data.split(":")[1]
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        await callback.answer("Тариф не найден.", show_alert=True)
        return

    user = await db.get_user_by_telegram_id(callback.from_user.id)
    payload = f"sub_{user['id']}_{tariff_key}_{callback.message.message_id}"
    await db.create_payment(user["id"], "subscription", tariff["price"], payload)

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"Подписка: {tariff['name']}",
        description=f"Доступ к заданиям на {tariff['name']}",
        payload=payload,
        provider_token="",
        currency="RUB",
        prices=[LabeledPrice(label=tariff["name"], amount=tariff["price"])],
        start_parameter=f"sub_{tariff_key}"
    )
    await callback.answer()
