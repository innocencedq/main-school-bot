from aiogram.fsm.state import State, StatesGroup


class ValentineProcess(StatesGroup):
    waiting_username = State()
    waiting_message = State()


class ReactValentines(StatesGroup):
    waiting_message = State()