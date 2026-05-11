"""Логика заказчика"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import db
from config import CATEGORIES, TASK_PRICE, CATEGORY_CHANNELS
from keyboards.inline import categories_keyboard, confirm_task_keyboard
from keyboards.reply import main_customer_keyboard, skip_keyboard, cancel_keyboard
from utils.states import CustomerFlow
from utils.notifications import notify_executors_about_task

router = Router()


@router.message(F.text == "📝 Создать задание")
async def create_task_start(message: Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user or user["role"] != "customer":
        await message.answer("Сначала выберите роль Заказчика через /start")
        return
    await message.answer(
        "Выберите категорию задания:",
        reply_markup=categories_keyboard()
    )
    await state.set_state(CustomerFlow.choosing_category)


@router.callback_query(CustomerFlow.choosing_category, F.data.startswith("cat:"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    cat_name = callback.data.split(":", 1)[1]
    category = await db.get_category_by_name(cat_name)
    await state.update_data(category_id=category["id"], category_name=cat_name)
    await callback.message.edit_text("Введите название задания:")
    await state.set_state(CustomerFlow.entering_title)
    await callback.answer()


@router.message(CustomerFlow.entering_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задания (ТЗ):")
    await state.set_state(CustomerFlow.entering_description)


@router.message(CustomerFlow.entering_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "Укажите бюджет (можно пропустить):",
        reply_markup=skip_keyboard()
    )
    await state.set_state(CustomerFlow.entering_budget)


@router.message(CustomerFlow.entering_budget)
async def process_budget(message: Message, state: FSMContext):
    budget = None if message.text == "⏭ Пропустить" else message.text
    await state.update_data(budget=budget)
    await message.answer(
        "Укажите сроки (можно пропустить):",
        reply_markup=skip_keyboard()
    )
    await state.set_state(CustomerFlow.entering_deadline)


@router.message(CustomerFlow.entering_deadline)
async def process_deadline(message: Message, state: FSMContext):
    deadline = None if message.text == "⏭ Пропустить" else message.text
    await state.update_data(deadline=deadline)
    await message.answer(
        "Прикрепите файлы (если нужно) или нажмите 'Пропустить':",
        reply_markup=skip_keyboard()
    )
    await state.set_state(CustomerFlow.attaching_files)


@router.message(CustomerFlow.attaching_files)
async def process_files(message: Message, state: FSMContext):
    file_ids = []
    if message.text != "⏭ Пропустить":
        if message.document:
            file_ids.append(message.document.file_id)
        elif message.photo:
            file_ids.append(message.photo[-1].file_id)

    await state.update_data(file_ids=",".join(file_ids) if file_ids else None)
    data = await state.get_data()

    preview = (
        f"📋 <b>Предпросмотр задания</b>\n\n"
        f"<b>Название:</b> {data['title']}\n"
        f"<b>Описание:</b> {data['description']}\n"
        f"<b>Бюджет:</b> {data.get('budget') or 'Не указан'}\n"
        f"<b>Сроки:</b> {data.get('deadline') or 'Не указаны'}\n"
        f"<b>Категория:</b> {data['category_name']}"
    )
    await message.answer(preview, reply_markup=confirm_task_keyboard(), parse_mode="HTML")
    await state.set_state(CustomerFlow.confirming)


@router.callback_query(CustomerFlow.confirming, F.data == "task:confirm")
async def confirm_task(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = await db.get_user_by_telegram_id(callback.from_user.id)

    # Создаём платёж
    payload = f"task_{user['id']}_{callback.message.message_id}"
    await db.create_payment(user["id"], "task", TASK_PRICE, payload)

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Публикация задания",
        description=f"Задание: {data['title'][:50]}",
        payload=payload,
        provider_token="",  # Укажите токен в config.py
        currency="RUB",
        prices=[LabeledPrice(label="Публикация", amount=TASK_PRICE)],
        start_parameter="create_task"
    )
    await callback.answer()


@router.callback_query(CustomerFlow.confirming, F.data == "task:cancel")
async def cancel_task(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Создание задания отменено.")
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot):
    payload = message.successful_payment.invoice_payload
    payment = await db.get_payment_by_payload(payload)
    if not payment:
        await message.answer("Ошибка: платёж не найден.")
        return

    await db.confirm_payment(payload)
    user = await db.get_user_by_id(payment["user_id"])

    if payment["type"] == "task":
        # Получаем данные задания из состояния (упрощённо — в реальном проекте храните в БД)
        # Здесь создаём задание с минимальными данными
        # В полноценной реализации нужно сохранять черновик задания в БД до оплаты
        await message.answer(
            "✅ Оплата прошла успешно! Задание опубликовано.",
            reply_markup=main_customer_keyboard()
        )
    elif payment["type"] == "resume":
        await message.answer(
            "✅ Оплата прошла успешно! Резюме опубликовано.",
            reply_markup=main_executor_keyboard()
        )
    elif payment["type"] == "subscription":
        from config import TARIFFS
        tariff_key = payload.split("_")[-1]
        tariff = TARIFFS.get(tariff_key)
        if tariff:
            await db.create_subscription(user["id"], tariff_key, tariff["days"])
            await db.apply_referral_bonus(user["id"])
            await message.answer(
                f"✅ Подписка '{tariff['name']}' активирована!",
                reply_markup=main_executor_keyboard()
            )


@router.message(F.text == "📋 Мои задания")
async def my_tasks(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    # Упрощённый вывод
    await message.answer("Функция 'Мои задания' в разработке.")


@router.message(F.text == "💳 Баланс")
async def my_balance(message: Message):
    await message.answer("Функция 'Баланс' в разработке.")
