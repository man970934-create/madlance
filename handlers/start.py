"""Старт и выбор роли"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.inline import role_choice_keyboard, change_role_keyboard
from keyboards.reply import main_customer_keyboard, main_executor_keyboard
from utils.states import RoleChoice

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user = await db.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    # Проверяем реферальную ссылку
    args = message.text.split()[1] if len(message.text.split()) > 1 else None
    if args and args.startswith("ref"):
        try:
            referrer_tg_id = int(args.replace("ref", ""))
            referrer = await db.get_user_by_telegram_id(referrer_tg_id)
            if referrer and referrer["id"] != user["id"]:
                await db.add_referral(referrer["id"], user["id"])
                await db.apply_referral_bonus(user["id"])
                await bot.send_message(
                    referrer_tg_id,
                    "🎉 По вашей ссылке зарегистрировался новый пользователь! +24 часа подписки!"
                )
        except (ValueError, TypeError):
            pass

    if user["role"] == "none":
        await message.answer(
            "Привет! 👋\n"
            "Добро пожаловать на фриланс-площадку!\n\n"
            "Выберите свою роль:",
            reply_markup=role_choice_keyboard()
        )
        await state.set_state(RoleChoice.choosing)
    elif user["role"] == "customer":
        await message.answer(
            "С возвращением! 👋\nВы в роли Заказчика.",
            reply_markup=main_customer_keyboard()
        )
    elif user["role"] == "executor":
        await message.answer(
            "С возвращением! 👋\nВы в роли Исполнителя.",
            reply_markup=main_executor_keyboard()
        )


@router.callback_query(F.data == "role:change")
@router.message(F.text == "🔄 Сменить роль")
async def change_role(event, state: FSMContext):
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            "Выберите свою роль:",
            reply_markup=role_choice_keyboard()
        )
    else:
        await event.answer(
            "Выберите свою роль:",
            reply_markup=role_choice_keyboard()
        )
    await state.set_state(RoleChoice.choosing)


@router.callback_query(RoleChoice.choosing, F.data.startswith("role:"))
async def process_role_choice(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":")[1]
    user = await db.get_user_by_telegram_id(callback.from_user.id)
    await db.set_user_role(user["id"], role)
    await state.clear()

    if role == "customer":
        await callback.message.edit_text(
            "Отлично! Вы выбрали роль Заказчика.\n\n"
            "Теперь вы можете создавать задания и находить исполнителей.",
        )
        await callback.message.answer(
            "Главное меню:",
            reply_markup=main_customer_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Отлично! Вы выбрали роль Исполнителя.\n\n"
            "Выберите интересующие категории и оформите подписку.",
        )
        await callback.message.answer(
            "Главное меню:",
            reply_markup=main_executor_keyboard()
        )
    await callback.answer()
