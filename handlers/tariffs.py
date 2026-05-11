"""Тарифы и оплата подписок"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext

from database import db
from config import TARIFFS
from keyboards.inline import payment_method_keyboard, tariffs_keyboard
from keyboards.reply import main_executor_keyboard
from utils.payments import crypto_bot, yoo_kassa

router = Router()


@router.callback_query(F.data == "show_tariffs")
async def show_tariffs_menu(callback: CallbackQuery):
    """Показать выбор тарифа"""
    await callback.message.edit_text(
        "📋 <b>Выберите тариф подписки:</b>\n\n"
        "🗓 Неделя — 200 ₽\n"
        "🗓 Месяц — 600 ₽\n"
        "🗓 3 месяца — 1400 ₽\n\n"
        "Выберите тариф:",
        reply_markup=tariffs_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("tariff:"))
async def process_tariff(callback: CallbackQuery):
    """Выбор способа оплаты тарифа"""
    tariff_key = callback.data.split(":")[1]
    tariff = TARIFFS.get(tariff_key)
    
    if not tariff:
        await callback.answer("Тариф не найден.", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"💳 <b>Оплата тарифа: {tariff['name']}</b>\n"
        f"Сумма: {tariff['price']} ₽\n\n"
        "Выберите способ оплаты:",
        reply_markup=payment_method_keyboard(f"sub_{tariff_key}"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("pay_crypto:"))
async def pay_with_crypto(callback: CallbackQuery, bot: Bot):
    """Оплата через CryptoBot"""
    if not crypto_bot:
        await callback.answer("CryptoBot временно недоступен", show_alert=True)
        return
    
    # Определяем тип и параметры платежа
    payment_type = callback.data.split(":")[1]
    
    if payment_type.startswith("sub_"):
        tariff_key = payment_type.replace("sub_", "")
        tariff = TARIFFS.get(tariff_key)
        if not tariff:
            await callback.answer("Ошибка тарифа", show_alert=True)
            return
        amount = float(tariff["price"])
        description = f"Подписка: {tariff['name']}"
        
    elif payment_type == "task":
        from config import TASK_PRICE
        amount = float(TASK_PRICE)
        description = "Публикация задания"
        
    elif payment_type == "resume":
        from config import RESUME_PRICE
        amount = float(RESUME_PRICE)
        description = "Публикация резюме"
    else:
        await callback.answer("Неизвестный тип платежа", show_alert=True)
        return
    
    # Создаем счет в CryptoBot
    invoice = await crypto_bot.create_invoice(
        amount=amount,
        description=description
    )
    
    if invoice:
        user = await db.get_user_by_telegram_id(callback.from_user.id)
        
        # Сохраняем платеж в БД
        from database import db
        await db.create_payment(
            user["id"],
            payment_type,
            int(amount),
            f"crypto_{invoice['invoice_id']}"
        )
        
        # Отправляем ссылку на оплату
        await callback.message.edit_text(
            f"💎 <b>Счет в CryptoBot создан!</b>\n\n"
            f"📋 Описание: {description}\n"
            f"💰 Сумма: {amount} ₽\n\n"
            f"🔗 <a href='{invoice['pay_url']}'>Нажмите для оплаты</a>\n\n"
            f"ID счета: <code>{invoice['invoice_id']}</code>\n\n"
            "После оплаты нажмите кнопку проверки:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔄 Проверить оплату",
                    callback_data=f"check_crypto:{invoice['invoice_id']}:{payment_type}"
                )],
                [InlineKeyboardButton(text="« Назад", callback_data="show_tariffs")]
            ]),
            parse_mode="HTML"
        )
    else:
        await callback.answer("Ошибка создания счета. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data.startswith("check_crypto:"))
async def check_crypto_payment(callback: CallbackQuery):
    """Проверка оплаты через CryptoBot"""
    parts = callback.data.split(":")
    invoice_id = parts[1]
    payment_type = parts[2]
    
    invoice = await crypto_bot.get_invoice(int(invoice_id))
    
    if invoice and invoice.get("status") == "paid":
        await db.confirm_payment(f"crypto_{invoice_id}")
        
        # Активируем услугу
        user = await db.get_user_by_telegram_id(callback.from_user.id)
        
        if payment_type.startswith("sub_"):
            tariff_key = payment_type.replace("sub_", "")
            tariff = TARIFFS.get(tariff_key)
            if tariff:
                await db.create_subscription(user["id"], tariff_key, tariff["days"])
                await db.apply_referral_bonus(user["id"])
                await callback.message.edit_text(
                    f"✅ <b>Оплата получена!</b>\n\n"
                    f"Подписка '{tariff['name']}' активирована!",
                    parse_mode="HTML"
                )
        else:
            await callback.message.edit_text(
                "✅ <b>Оплата получена!</b>\n\nУслуга активирована.",
                parse_mode="HTML"
            )
    else:
        await callback.answer("Платеж еще не получен. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data.startswith("pay_yookassa:"))
async def pay_with_yookassa(callback: CallbackQuery, bot: Bot):
    """Оплата через ЮKassa"""
    if not yoo_kassa:
        await callback.answer("ЮKassa временно недоступна", show_alert=True)
        return
    
    payment_type = callback.data.split(":")[1]
    
    if payment_type.startswith("sub_"):
        tariff_key = payment_type.replace("sub_", "")
        tariff = TARIFFS.get(tariff_key)
        if not tariff:
            await callback.answer("Ошибка тарифа", show_alert=True)
            return
        amount = float(tariff["price"])
        description = f"Подписка: {tariff['name']}"
    elif payment_type == "task":
        amount = float(TASK_PRICE)
        description = "Публикация задания"
    elif payment_type == "resume":
        amount = float(RESUME_PRICE)
        description = "Публикация резюме"
    else:
        await callback.answer("Неизвестный тип платежа", show_alert=True)
        return
    
    # Создаем платеж в ЮKassa
    payment = await yoo_kassa.create_payment(
        amount=amount,
        description=description
    )
    
    if payment:
        user = await db.get_user_by_telegram_id(callback.from_user.id)
        await db.create_payment(
            user["id"],
            payment_type,
            int(amount * 100),  # в копейках
            f"yookassa_{payment['id']}"
        )
        
        await callback.message.edit_text(
            f"💳 <b>Платеж в ЮKassa создан!</b>\n\n"
            f"📋 Описание: {description}\n"
            f"💰 Сумма: {amount} ₽\n\n"
            f"🔗 <a href='{payment['confirmation']['confirmation_url']}'>Перейти к оплате</a>\n\n"
            "После оплаты нажмите кнопку проверки:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔄 Проверить оплату",
                    callback_data=f"check_yookassa:{payment['id']}:{payment_type}"
                )],
                [InlineKeyboardButton(text="« Назад", callback_data="show_tariffs")]
            ]),
            parse_mode="HTML"
        )
    else:
        await callback.answer("Ошибка создания платежа", show_alert=True)


@router.callback_query(F.data.startswith("check_yookassa:"))
async def check_yookassa_payment(callback: CallbackQuery):
    """Проверка оплаты через ЮKassa"""
    parts = callback.data.split(":")
    payment_id = parts[1]
    payment_type = parts[2]
    
    payment = await yoo_kassa.check_payment(payment_id)
    
    if payment and payment.get("status") == "succeeded":
        await db.confirm_payment(f"yookassa_{payment_id}")
        
        user = await db.get_user_by_telegram_id(callback.from_user.id)
        
        if payment_type.startswith("sub_"):
            tariff_key = payment_type.replace("sub_", "")
            tariff = TARIFFS.get(tariff_key)
            if tariff:
                await db.create_subscription(user["id"], tariff_key, tariff["days"])
                await db.apply_referral_bonus(user["id"])
                await callback.message.edit_text(
                    f"✅ <b>Оплата получена!</b>\n\n"
                    f"Подписка '{tariff['name']}' активирована!",
                    parse_mode="HTML"
                )
        else:
            await callback.message.edit_text(
                "✅ <b>Оплата получена!</b>\n\nУслуга активирована.",
                parse_mode="HTML"
            )
    else:
        await callback.answer("Платеж еще не завершен. Попробуйте позже.", show_alert=True)
