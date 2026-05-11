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

# ЮKassa
YOO_KASSA_SHOP_ID = os.getenv("YOO_KASSA_SHOP_ID")
YOO_KASSA_SECRET_KEY = os.getenv("YOO_KASSA_SECRET_KEY")

# CryptoBot
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
CRYPTOBOT_API_URL = "https://pay.crypt.bot/api"

# Channels mapping
CATEGORY_CHANNELS = {
    "Веб-дизайн": "@vakansii_design",
    "Копирайтинг": "@vakansii_copy",
    "SMM": "@vakansii_smm",
    "Видео/Монтаж": "@vakansii_reels",
    "Тех.Спец/Боты": "@vakansii_tehspec",
    "Маркетинг": "@vakansii_target",
    "Дизайн/Иллюстрации": "@vakansii_design",
    "Другое": None,
}

CATEGORIES = list(CATEGORY_CHANNELS.keys())

# Tariffs (цены в копейках для ЮKassa и RUB для CryptoBot)
TARIFFS = {
    "week": {"name": "Неделя", "price": 200, "price_kop": 20000, "days": 7, "label": "200 ₽"},
    "month": {"name": "Месяц", "price": 600, "price_kop": 60000, "days": 30, "label": "600 ₽"},
    "quarter": {"name": "3 месяца", "price": 1400, "price_kop": 140000, "days": 90, "label": "1400 ₽"},
}

# Prices in RUB (для CryptoBot) and kopecks (для ЮKassa)
TASK_PRICE = 100  # RUB
TASK_PRICE_KOP = 10000  # копеек
RESUME_PRICE = 100  # RUB
RESUME_PRICE_KOP = 10000  # копеек

# Referral bonus (hours)
REFERRAL_BONUS_HOURS = 24

# Task/Resume lifetime (days)
PUBLICATION_LIFETIME_DAYS = 90
