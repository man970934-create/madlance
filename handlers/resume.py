"""Размещение резюме"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext

from database import db
from config import RESUME_PRICE, CATEGORY_CHANNELS
from keyboards.inline import categories_keyboard, confirm_resume_keyboard
from keyboards.reply import main_executor_keyboard
from utils.states import ResumeFlow

router = Router()


@router.message(F.text == "💼 Разместить резюме")
async def create_resume_start(message: Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user or user["role"] != "executor":
        await message.answer("Сначала выберите роль Исполнителя через /start")
        return
    await message.answer(
        "Выберите категорию для резюме:",
        reply_markup=categories_keyboard()
    )
    await state.set_state(ResumeFlow.choosing_category)


@router.callback_query(ResumeFlow.choosing_category, F.data.startswith("cat:"))
async def process_resume_category(callback: CallbackQuery, state: FSMContext):
    cat_name = callback.data.split(":", 1)[1]
    category = await db.get_category_by_name(cat_name)
    await state.update_data(category_id=category["id"], category_name=cat_name)
    await callback.message.edit_text("Введите текст резюме (опишите свой опыт и навыки):")
    await state.set_state(ResumeFlow.entering_content)
    await callback.answer()


@router.message(ResumeFlow.entering_content)
async def process_resume_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    data = await state.get_data()
    preview = (
        f"📄 <b>Предпросмотр резюме</b>\n\n"
        f"<b>Категория:</b> {data['category_name']}\n"
        f"<b>Описание:</b>\n{data['content']}"
    )
    await message.answer(preview, reply_markup=confirm_resume_keyboard(), parse_mode="HTML")
    await state.set_state(ResumeFlow.confirming)


@router.callback_query(ResumeFlow.confirming, F.data == "resume:confirm")
async def confirm_resume(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user = await db.get_user_by_telegram_id(callback.from_user.id)
    payload = f"resume_{user['id']}_{callback.message.message_id}"
    await db.create_payment(user["id"], "resume", RESUME_PRICE, payload)

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Публикация резюме",
        description="Публикация резюме на 3 месяца",
        payload=payload,
        provider_token="",
        currency="RUB",
        prices=[LabeledPrice(label="Резюме", amount=RESUME_PRICE)],
        start_parameter="create_resume"
    )
    await callback.answer()


@router.callback_query(ResumeFlow.confirming, F.data == "resume:cancel")
async def cancel_resume(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Размещение резюме отменено.")
    await callback.answer()
