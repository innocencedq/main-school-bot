from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ScheduleChangerKeyboard:
    @staticmethod
    def list_shift(method: str):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='1 смена', callback_data=f'week_first_shift:{method}')],
            [InlineKeyboardButton(text='2 смена', callback_data=f'week_second_shift:{method}')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='adminpanel')],
            ])

    @staticmethod
    def week_changer(shift: str):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Понедельник', callback_data=f'changer:monday:{shift}')],
            [InlineKeyboardButton(text='Вторник', callback_data=f'changer:tuesday:{shift}')],
            [InlineKeyboardButton(text='Среда', callback_data=f'changer:wednesday:{shift}')],
            [InlineKeyboardButton(text='Четверг', callback_data=f'changer:thursday:{shift}')],
            [InlineKeyboardButton(text='Пятница', callback_data=f'changer:friday:{shift}')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'day_change')],
            ])
    

