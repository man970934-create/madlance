"""Регистрация хендлеров"""
from aiogram import Dispatcher
from .start import router as start_router
from .customer import router as customer_router
from .executor import router as executor_router
from .resume import router as resume_router
from .tariffs import router as tariffs_router
from .referral import router as referral_router
from .help import router as help_router
from .admin import router as admin_router


def register_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(customer_router)
    dp.include_router(executor_router)
    dp.include_router(resume_router)
    dp.include_router(tariffs_router)
    dp.include_router(referral_router)
    dp.include_router(help_router)
    dp.include_router(admin_router)
