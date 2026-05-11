"""Точка входа бота"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import db
from handlers import register_handlers
from utils.scheduler import scheduler_loop

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация БД
    await db.init_db()
    from config import CATEGORY_CHANNELS
    await db.init_categories(CATEGORY_CHANNELS)

    # Регистрация хендлеров
    register_handlers(dp)

    # Запуск планировщика
    asyncio.create_task(scheduler_loop())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())