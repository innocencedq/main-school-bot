from aiogram.fsm.state import State, StatesGroup


class TechSup(StatesGroup):
    waiting_idea = State()
    waiting_bug = State()