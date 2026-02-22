from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton


import app.database.requests as req
import app.components.routers.valentine_day.keyboard as kb
import app.components.routers.valentine_day.states as St


router = Router()


@router.callback_query(F.data == 'valentine_day')
async def main_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await state.clear()
    unread_count = await req.get_unread_valentines(user_id)
    notify_text = ''

    if unread_count != 0:
        notify_text = f"📬 У вас <b>{unread_count}</b> непрочитанн{['ая','их','ых'][0 if unread_count%10==1 and unread_count%100!=11 else 1 if unread_count%10 in[2,3,4]and unread_count%100 not in[12,13,14]else 2]} валентинк{[['а','и',''][0 if unread_count%10==1 and unread_count%100!=11 else 1 if unread_count%10 in[2,3,4]and unread_count%100 not in[12,13,14]else 2]][0]}!\n\n"

    image = await req.get_image('valentine')
    photo = InputMediaPhoto(media=image,
                            caption='<b>📮 День святого Валентина.</b>\n\n' \
                                    '<b>🔹 Здесь ты можешь:</b>\n' \
                                    '• Отправить валентинку <b>любому</b> человеку\n' \
                                    '• Настроить, хочешь ли ты получать валентинки\n' \
                                    '• Реагировать или получать реакцию на отправленные валентинки\n\n' 
                                    f'{notify_text}'\
                                    'Выбери действие ниже ⤵️',
                            parse_mode='html')

    await callback.message.edit_media(media=photo,
                                      reply_markup=await kb.main_valentine(user_id, callback.from_user.first_name))
    

@router.callback_query(F.data.startswith('valentine:'))
async def reproccess_tasks(callback: CallbackQuery, state: FSMContext):
    args = callback.data.split(':')

    if args[1] == 'send_valentine':
        image = await req.get_image('send_valentine')
        photo = InputMediaPhoto(media=image,
                                caption='💌 <b>Напишите юзернейм получателя</b>\n\nВы можете указать его в любом удобном формате: @username, ссылка или просто текст.',
                                parse_mode='html')

        await callback.message.edit_media(media=photo, 
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                          [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine_day', style='primary')]
                                          ]))
        await state.set_state(St.ValentineProcess.waiting_username)
    elif args[1] == 'my_valentines':
        if args[2] == '0':
            await callback.answer('😔 У вас пока нет валентинок...', True)
        else:
            await my_valentines(callback, args[2], state)
    elif args[1] == 'react_valentine':
        await callback.message.edit_caption(caption='💬 <b>Реакция на валентинку</b>\n\nНапишите ответное сообщение или реакцию. Это может быть текст, стикер или голосовое сообщение. <a href="https://telegra.ph/Podderzhivaemye-formaty-02-05">Поддерживаемые форматы</a>',
                                            parse_mode='html',
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'valentine:my_valentines:{args[3]}', style='primary')]
                                            ]))
        await state.set_data({"sender_id": args[2], "receiver_id": args[4], "valentine_id": args[3]})
        await state.set_state(St.ReactValentines.waiting_message)
    elif args[1] == 'profile':
        if len(args) > 2 and args[2] == 'change_allow':
            await req.change_allow_valentines(callback.from_user.id)

        chat_id = callback.from_user.id
        first_name = callback.from_user.first_name
        data = await req.get_full_info_user(chat_id)
        status_valentine = data.get('allow_valentines')
        count_sents, count_received = await req.get_user_for_profile_info(chat_id)


        await callback.message.edit_caption(caption=f'👤 <b>{first_name}</b>\n\n'
                                            f'📤 Отправлено валентинок: <b>{count_sents}</b>\n'
                                            f'📥 Получено валентинок: <b>{count_received}</b>\n\n'
                                            f'🔐 <b>Настройки приватности:</b>\n'
                                            + ('✅ Вы <b>разрешаете</b> получать валентинки' if status_valentine else '❌ Вы <b>запрещаете</b> получать валентинки'),
                                            parse_mode='html',
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text='❌ Запретить валентинки' if status_valentine else '✅ Разрешить валентинки',
                                                                      callback_data='valentine:profile:change_allow')],
                                                [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'valentine_day', style='primary')]
                                            ]))
        

async def my_valentines(callback: CallbackQuery, valentine_id: int, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    data = await req.get_info_about_valentine(valentine_id)
    
    await req.update_reading_valentine(valentine_id)
    unread_count = await req.get_unread_valentines(user_id)

    receiver_id = data.get('receiver_id')
    sender_id = data.get('sender_id')
    message = data.get('message')
    may_react = data.get('may_react')

    response_text = "📩 <b>Мои валентинки</b>\n\n"

    if unread_count != 0:
        response_text += f"📬 У вас еще <b>{unread_count}</b> непрочитанн{['ая','их','ых'][0 if unread_count%10==1 and unread_count%100!=11 else 1 if unread_count%10 in[2,3,4]and unread_count%100 not in[12,13,14]else 2]} валентинк{[['а','и',''][0 if unread_count%10==1 and unread_count%100!=11 else 1 if unread_count%10 in[2,3,4]and unread_count%100 not in[12,13,14]else 2]][0]}!"
    
    response_text += f"💌 <b>Сообщение:</b>\n{message}\n\n"
    
    if may_react == True:
        response_text += "💬 Вы можете ответить на эту валентинку"


    image = await req.get_image('my_valentines')
    photo = InputMediaPhoto(media=image,
                            caption=response_text,
                            parse_mode='html')
    await callback.message.edit_media(media=photo,
                                      reply_markup=await kb.valentine_scroller(curr_id=valentine_id, sender_id=sender_id, may_react=may_react, receiver_id=receiver_id))


