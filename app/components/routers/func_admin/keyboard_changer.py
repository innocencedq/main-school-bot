from functools import lru_cache
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.database.requests import get_user_with_notify, get_list_admin, get_quick_menu, get_user_with_extended_diary, check_admin, get_refresh_token, get_last_advert_id, get_list_open_tickets, get_shift
from app.supportfunctions.main_utils import get_day_name


class ScheduleChangerKeyboard:
    list_shift = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='1 смена', callback_data='week_first_shift')],
        [InlineKeyboardButton(text='2 смена', callback_data='week_second_shift')],
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
    

