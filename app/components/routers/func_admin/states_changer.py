from aiogram.fsm.state import State, StatesGroup

class FormChanger(StatesGroup):
    waiting_day = State()