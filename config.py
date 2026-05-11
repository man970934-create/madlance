"""Конфигурация бота"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# Payments
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/freelance_bot.db")

# Channels mapping: category -> channel_id or @username
CATEGORY_CHANNELS = {
    "Веб-дизайн": "@vakansii_design",
    "Копирайтинг": "@vakansii_copy",
    "SMM": "@vakansii_smm",
    "Видео/Монтаж": "@vakansii_reels",
    "Тех.Спец/Боты": "@vakansii_tehspec",
    "Маркетинг": "@vakansii_target",
    "Дизайн/Иллюстрации": "@vakansii_design",
    "Другое": None,  # Укажите канал или оставьте None
}

CATEGORIES = list(CATEGORY_CHANNELS.keys())

# Tariffs
TARIFFS = {
    "week": {"name": "Неделя", "price": 20000, "days": 7, "label": "200 ₽"},
    "month": {"name": "Месяц", "price": 60000, "days": 30, "label": "600 ₽"},
    "quarter": {"name": "3 месяца", "price": 140000, "days": 90, "label": "1400 ₽"},
}

# Prices (in kopecks for Telegram Payments)
TASK_PRICE = 10000       # 100 ₽
RESUME_PRICE = 10000     # 100 ₽

# Referral bonus (hours)
REFERRAL_BONUS_HOURS = 24

# Task/Resume lifetime (days)
PUBLICATION_LIFETIME_DAYS = 90
