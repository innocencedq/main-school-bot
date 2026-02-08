from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as req
from app.supportfunctions.main_utils import pagination


async def main_valentine(user_id, first_name):
    builder = InlineKeyboardBuilder()

    unread_val = await req.get_unread_valentines(user_id)
    data_ids = await req.get_ids_valentines(user_id)

    if data_ids:
        last_id = data_ids[-1]
    
    builder.add(InlineKeyboardButton(text=f'👤 {first_name}', callback_data='valentine:profile'))
    builder.add(InlineKeyboardButton(text='💌 Отправить валентинку', callback_data='valentine:send_valentine'))
    builder.add(InlineKeyboardButton(text='📩 Мои валентинки ' + (f'({unread_val})' if unread_val != 0 else ''), callback_data=f'valentine:my_valentines:{last_id if data_ids else 0}'))
    builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))

    return builder.adjust(1, 1).as_markup()


async def valentine_scroller(curr_id, sender_id, may_react, receiver_id):
    builder = InlineKeyboardBuilder()

    data_ids = await req.get_ids_valentines(receiver_id)

    next_id, prev_id, curr_idx = await pagination(data_ids, curr_id)
    all_pages = len(data_ids)
    
    adjust_param = 3

    if prev_id == None or next_id == None:
        adjust_param -= 1 if prev_id != next_id else 2

    builder.add(InlineKeyboardButton(text='⬅️',
                                     callback_data=f'valentine:my_valentines:{prev_id}')) if prev_id else None
    builder.add(InlineKeyboardButton(text=f'{abs(curr_idx - all_pages)}/{all_pages}', 
                                     callback_data='page'))
    builder.add(InlineKeyboardButton(text='➡️', 
                                     callback_data=f'valentine:my_valentines:{next_id}')) if next_id else None
    builder.add(InlineKeyboardButton(text='💬 Отреагировать',
                                     callback_data=f'valentine:react_valentine:{sender_id}:{curr_id}:{receiver_id}')) if may_react else None
    builder.add(InlineKeyboardButton(text='⬅️ Назад',
                                     callback_data='valentine_day'))
    
    return builder.adjust(adjust_param, 1, 1).as_markup()