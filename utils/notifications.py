"""Уведомления исполнителей о новых заданиях"""
from aiogram import Bot
from database import db
from keyboards.inline import task_action_keyboard


async def notify_executors_about_task(bot: Bot, task_id: int):
    task = await db.get_task(task_id)
    if not task:
        return

    category = await db.get_category_by_name(task["category_id"])
    # Получаем всех исполнителей с активной подпиской и выбранной категорией
    users = await db.get_all_users()

    text = (
        f"📌 <b>Новое задание!</b>\n\n"
        f"<b>{task['title']}</b>\n"
        f"{task['description'][:200]}{'...' if len(task['description']) > 200 else ''}\n\n"
        f"💰 Бюджет: {task['budget'] or 'Не указан'}\n"
        f"⏰ Срок: {task['deadline'] or 'Не указан'}\n"
        f"📁 Категория: {category['name'] if category else 'Неизвестно'}"
    )

    for user in users:
        if user["role"] != "executor":
            continue
        sub = await db.get_active_subscription(user["id"])
        if not sub:
            continue
        user_cats = await db.get_user_categories(user["id"])
        user_cat_ids = [c["id"] for c in user_cats]
        if task["category_id"] not in user_cat_ids:
            continue

        try:
            await bot.send_message(
                user["telegram_id"],
                text,
                reply_markup=task_action_keyboard(task_id),
                parse_mode="HTML"
            )
        except Exception:
            pass
