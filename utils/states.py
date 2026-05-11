"""FSM состояния"""
from aiogram.fsm.state import State, StatesGroup


class RoleChoice(StatesGroup):
    choosing = State()


class CustomerFlow(StatesGroup):
    choosing_category = State()
    entering_title = State()
    entering_description = State()
    entering_budget = State()
    entering_deadline = State()
    attaching_files = State()
    confirming = State()


class ExecutorFlow(StatesGroup):
    choosing_categories = State()
    choosing_tariff = State()
    viewing_task = State()


class ResumeFlow(StatesGroup):
    choosing_category = State()
    entering_content = State()
    confirming = State()


class TariffFlow(StatesGroup):
    choosing_country = State()
    choosing_tariff = State()
    paying = State()
