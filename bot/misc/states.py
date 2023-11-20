from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    post = State()
    post_datetime = State()
