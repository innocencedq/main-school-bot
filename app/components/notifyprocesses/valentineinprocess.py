from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

import app.database.requests as req
from app.components.logs.logs import logger

async def check_new_user_valentines_Message(message: Message):
    try:
        res = await req.change_tables_info_valentine(message.from_user.id, message.from_user.username)

        if res == 'has_valentines':
            valentine_list = await req.get_ids_valentines(message.from_user.id)
            last_valentine_id = valentine_list[-1]
            total_count = len(valentine_list)

            if total_count == 1:
                notification_text = "🕒 <b>Пока вас не было...</b>\n\n✨ Вам пришла новая валентинка!"
            else:
                if total_count % 10 == 1 and total_count % 100 != 11:
                    word = "валентинка"
                elif total_count % 10 in [2, 3, 4] and total_count % 100 not in [12, 13, 14]:
                    word = "валентинки"
                else:
                    word = "валентинок"
                
                notification_text = f"🕒 <b>Пока вас не было...</b>\n\n✨ Вам пришло <b>{total_count}</b> {word}!"

            await message.answer(text=notification_text, 
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='📖 Посмотреть', callback_data=f'valentine:my_valentines:{last_valentine_id}')],
                    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
                ]),
                                 parse_mode='html')
    except Exception as e:
        await logger.error(f'check_new_user_valentines_Message: {e}')
        pass


async def check_new_user_valentines_CallbackQuery(callback: CallbackQuery):
    try:
        res = await req.change_tables_info_valentine(callback.from_user.id, callback.from_user.username)

        if res == 'has_valentines':
            valentine_list = await req.get_ids_valentines(callback.from_user.id)
            last_valentine_id = valentine_list[-1]
            total_count = len(valentine_list)

            if total_count == 1:
                notification_text = "🕒 <b>Пока вас не было...</b>\n\n✨ Вам пришла новая валентинка!"
            else:
                if total_count % 10 == 1 and total_count % 100 != 11:
                    word = "валентинка"
                elif total_count % 10 in [2, 3, 4] and total_count % 100 not in [12, 13, 14]:
                    word = "валентинки"
                else:
                    word = "валентинок"
                
                notification_text = f"🕒 <b>Пока вас не было...</b>\n\n✨ Вам пришло <b>{total_count}</b> {word}!"

            await callback.message.answer(text=notification_text,
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='📖 Посмотреть', callback_data=f'valentine:my_valentines:{last_valentine_id}')],
                    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
                ]),
                                         parse_mode='html')
    except Exception as e:
        await logger.error(f'check_new_user_valentines_CallbackQuery: {e}')
        pass