from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration as hd


import app.components.routers.valentine_day.states as St
import app.database.requests as req
import app.supportfunctions.main_utils as utils

from app.components.logs.logs import logger
from app.supportfunctions.badwords_checker import SimpleProfanityFilter

router = Router()


@router.message(St.ValentineProcess.waiting_username)
async def preprocess_sending(message: Message, state: FSMContext):
    typeof = message.content_type
    
    if typeof != 'text':
        await message.answer(
            '📝 <b>Юзернейм должен быть текстом</b>\n\n'
            'Укажите юзернейм в одном из форматов:\n'
            '• @username\n'
            '• https://t.me/username\n'
            '• просто username\n\n'
            '<i>Если у пользователя нет юзернейма, то отправить не получится!</i>',
            parse_mode='html'
        )
        await state.set_state(St.ValentineProcess.waiting_username)
        return

    text = message.text
    await logger.info(text)

    if '@' in text:
        username = text.replace('@', '')
    elif 'https://t.me/' in text:
        username = text.replace('https://t.me/', '')
    else:
        username = text
    
    is_user = await req.is_user_exists(username, method='username')
    is_sended = await req.is_sending_before(username, message.from_user.id)

    if is_sended:
        await message.answer(
            '⚠️ <b>Вы уже отправляли валентинку этому пользователю</b>\n\n'
            'Пожалуйста, выберите другого получателя.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine_day')]
            ])
        )
        return

    if is_user:
        data = await req.get_full_info_user(username, method='username')
        chat_id = data.get('tg_id')
        is_allowed = await req.is_sending_allowed(chat_id)

        if is_allowed:
            await message.answer(
                '✅ <b>Пользователь найден!</b>\n\n'
                'Теперь напишите текст валентинки ✍️',
                parse_mode='html',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine:send_valentine')]
                ])
            )
            await state.set_state(St.ValentineProcess.waiting_message)
            await state.set_data({
                'method': 'exists',
                'receiver_id': chat_id
            })
        else:
            await message.answer(
                '❌ <b>Пользователь найден, но...</b>\n\n'
                'К сожалению, этот пользователь отключил получение валентинок.',
                parse_mode='html',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='📤 Отправить другому', callback_data='valentine:send_valentine')],
                    [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine_day')]
                ])
            )
    else:
        await message.answer(
            '🤔 <b>Пользователь не найден...</b>\n\n'
            'Не переживайте! Когда пользователь впервые запустит бота, '
            'он получит уведомление о вашей валентинке.\n\n'
            'Теперь напишите текст валентинки ✍️',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine_day')]
            ])
        )
        await state.set_state(St.ValentineProcess.waiting_message)
        await state.set_data({
            'method': 'notexists',
            'receiver_username': username
        })


@router.message(St.ValentineProcess.waiting_message)
async def processing_sending(message: Message, state: FSMContext):
    filter = SimpleProfanityFilter()
    typeof = message.content_type
    data = await state.get_data()

    if typeof != 'text':
        await message.answer(
            '📝 <b>Валентинка должна быть текстом</b>\n\n'
            'Пожалуйста, отправьте текстовое сообщение.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine:send_valentine')]
            ])
        )
        await state.set_state(St.ValentineProcess.waiting_message)
        return

    ents = message.entities or []
    text = message.text

    if data.get('method') == 'exists':
        receiver = data.get('receiver_id')
        method = 'id'
    else:  # method == 'notexists'
        receiver = data.get('receiver_username')
        method = 'username'

    res = await filter.check_text(message.text)

    if res['has_profanity']:
        await message.answer(
            '⚠️ <b>Давайте без грубостей...</b>\n\n'
            'Пожалуйста, напишите валентинку без грубостей и оскорблений.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine_day')]
            ])
        )
        await state.set_state(St.ValentineProcess.waiting_message)
        return

    text = hd.unparse(text, ents)
    res = await sending_valentine(
        method=method,
        receiver=receiver,
        sender=message.from_user.id,
        message=text
    )
    
    if res != 'failed':
        await message.answer(
            '💖 <b>Валентинка отправлена!</b>\n\n'
            'Теперь можно перейти назад или отправить еще одну, но другому человеку.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='📤 Отправить еще', callback_data='valentine:send_valentine')],
                [InlineKeyboardButton(text='🏠 На главную', callback_data='valentine_day')]
            ])
        )
    else:
        await message.answer(
            '❌ <b>Не удалось отправить валентинку</b>\n\n'
            'Произошла техническая ошибка. Мы уже уведомили администратора.\n'
            'Попробуйте позже.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ Назад', callback_data='valentine_day')]
            ])
        )


@router.message(St.ReactValentines.waiting_message)
async def proccess_react(message: Message, state: FSMContext):
    data = await state.get_data()
    sender_id = data.get('sender_id')
    receive_id = data.get('receiver_id')
    valentine_id = data.get('valentine_id')
    data_user = await req.get_full_info_user(sender_id)
    username_sender = data_user.get('username')
    image = await req.get_image('my_valentines')
    
    keyboard_exit = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
    ])

    allowed_types = ['text', 'photo', 'video', 'voice', 'sticker', 'audio']
    
    try:
        from run import bot
        
        if message.content_type not in allowed_types:
            await message.answer(
                '⚠️ <b>Неподдерживаемый формат</b>\n\n'
                'Доступные форматы для реакции:\n'
                '• 📝 Текст\n'
                '• 🎤 Голосовое сообщение\n'
                '• 📷 Фотография/Видео\n'
                '• 🎵 Аудиофайл\n'
                '• 🤡 Стикер\n\n'
                'Пожалуйста, выберите один из этих форматов.',
                parse_mode='html',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
                ])
            )
            await state.set_state(St.ReactValentines.waiting_message)
            return

        notification_text = f"💌 <b>На вашу валентинку отреагировали!</b>\n\nОтправитель: @{username_sender}"
        
        if message.text:
            await bot.send_message(
                chat_id=sender_id,
                text=f"{notification_text}\n\n💬 <b>Сообщение:</b>\n{message.text[:1000]}",
                parse_mode='html',
                reply_markup=keyboard_exit
            )
            await req.update_rights_react(valentine_id)
            await logger.info(f'{receive_id} отреагировал на валентинку {sender_id} текстом: {message.text[:1000]}')

        elif message.photo:
            await bot.send_message(
                chat_id=sender_id,
                text=notification_text,
                parse_mode='html',
                reply_markup=keyboard_exit
            )
            await bot.send_photo(
                chat_id=sender_id,
                photo=message.photo[-1].file_id,
                caption=message.caption[:600] if message.caption else None,
                reply_markup=keyboard_exit
            )
            await req.update_rights_react(valentine_id)
            await logger.info(f'{receive_id} отреагировал на валентинку {sender_id} фото {message.photo[-1].file_id}, Описание: {message.caption}')

        elif message.video:
            await bot.send_message(
                chat_id=sender_id,
                text=notification_text,
                parse_mode='html',
                reply_markup=keyboard_exit
            )
            await bot.send_video(
                chat_id=sender_id,
                video=message.video.file_id,
                caption=message.caption[:600] if message.caption else None,
                reply_markup=keyboard_exit
            )
            await req.update_rights_react(valentine_id)
            await logger.info(f'{receive_id} отреагировал на валентинку {sender_id} видео {message.video.file_id}, Описание: {message.caption}')

        elif message.voice:
            await bot.send_message(
                chat_id=sender_id,
                text=f"{notification_text}\n\n🎤 <b>Голосовое сообщение:</b>",
                parse_mode='html',
                reply_markup=keyboard_exit
            )
            await bot.send_voice(
                chat_id=sender_id,
                voice=message.voice.file_id,
                reply_markup=keyboard_exit
            )
            await req.update_rights_react(valentine_id)
            await logger.info(f'{receive_id} отреагировал на валентинку {sender_id} голосовым сообщением {message.voice.file_id}')

        elif message.sticker:
            await bot.send_message(
                chat_id=sender_id,
                text=notification_text,
                parse_mode='html',
                reply_markup=keyboard_exit
            )
            await bot.send_sticker(
                chat_id=sender_id,
                sticker=message.sticker.file_id,
                reply_markup=keyboard_exit
            )
            await req.update_rights_react(valentine_id)
            await logger.info(f'{receive_id} отреагировал на валентинку {sender_id} стикером {message.sticker.file_id}')

        elif message.audio:
            await bot.send_message(
                chat_id=sender_id,
                text=notification_text,
                parse_mode='html',
                reply_markup=keyboard_exit
            )
            await bot.send_audio(
                chat_id=sender_id,
                audio=message.audio.file_id,
                caption=message.caption[:600] if message.caption else None,
                reply_markup=keyboard_exit
            )
            await req.update_rights_react(valentine_id)
            await logger.info(f'{receive_id} отреагировал на валентинку {sender_id} аудио {message.audio.file_id}, Описание: {message.caption}')

        # Подтверждение пользователю
        await message.answer_photo(
            photo=image, 
            caption='✅ <b>Реакция отправлена!</b>\n\n'
                   'Отправитель валентинки получил ваше сообщение.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ К валентинкам', callback_data=f'valentine:my_valentines:{valentine_id}')]
            ])
        )
        await state.clear()
        
    except Exception as e:
        await message.answer_photo(
            photo=image, 
            caption='❌ <b>Не удалось отправить реакцию</b>\n\n'
                   'Произошла техническая ошибка. Мы уже уведомили администратора.\n'
                   'Попробуйте позже.',
            parse_mode='html',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬅️ К валентинкам', callback_data=f'valentine:my_valentines:{valentine_id}')]
            ])
        )
        await state.clear()
        await logger.error(f'Ошибка в proccess_react: {e}')
        await utils.send_error_to_adm(f'Ошибка в proccess_react\n\n{e}')
        return 'failed'


async def sending_valentine(method: str, receiver, sender, message):
    try:
        if method == 'id':
            valentine_id = await req.create_valentine_user(
                receiver_id=receiver,
                sender_id=sender,
                message=message,
                method=method
            )

            from run import bot
            await bot.send_message(
                chat_id=receiver,
                text='💌 <b>Вам пришла новая валентинка!</b>\n\n'
                     'Кто-то отправил вам сердечное послание 💖',
                parse_mode='html',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='📖 Посмотреть', callback_data=f'valentine:my_valentines:{valentine_id}')]
                ])
            )
            
            await logger.info(f'{sender} отправил валентинку {receiver}: {message}')

            return 'success'
            
        elif method == 'username':
            await req.create_valentine_user(
                receiver_id=receiver,
                sender_id=sender,
                message=message,
                method=method
            )
            
            await logger.info(f'{sender} отправил валентинку {receiver}: {message}')

            return 'success'
            
    except Exception as e:
        await logger.error(f'Ошибка в sending_valentine: {e}')
        await utils.send_error_to_adm(f'Ошибка в sending_valentine\n\n{e}')
        return 'failed'