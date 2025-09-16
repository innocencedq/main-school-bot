from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import woman_day

async def events_keyboard():
    builder = InlineKeyboardBuilder()
    if woman_day == 1:
        builder.add(InlineKeyboardButton(text='🌸 День женщин', callback_data='woman_day_menu'))
        builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))
    else:
        builder.add(InlineKeyboardButton(text='🤖 ИИ', callback_data='week_ai'))
        builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))

    return builder.adjust(1).as_markup()


woman_day_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Начать', callback_data='woman_day')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='events')],

])

woman_day_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='woman_day_menu')],

])

are_u_sure = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Да', callback_data='yes_valentine')],
    [InlineKeyboardButton(text='❌ Нет', callback_data='woman_day_menu')]
])

report = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⛔️ Пожаловаться', callback_data='reporting')],
    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
])