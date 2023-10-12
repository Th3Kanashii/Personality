from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    notification = State()
    notification_time = State()
