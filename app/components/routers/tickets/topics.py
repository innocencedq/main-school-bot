from aiogram import Router, F
from aiogram.types import Message
from aiogram.methods import CreateForumTopic, EditForumTopic, CloseForumTopic

import app.database.requests as req

topic_router = Router()

CHAT_ID = -1002747010760
OPEN_EMOJI_ID = '5377316857231450742'
CLOSED_EMOJI_ID = '5237699328843200968'

async def create_topic(id, message, username, tg_id):
    from run import bot
    data = await bot(CreateForumTopic(chat_id=CHAT_ID, name=f'📄 Тикет #{id}'))
    await bot(EditForumTopic(chat_id=CHAT_ID, message_thread_id=data.message_thread_id, icon_custom_emoji_id=OPEN_EMOJI_ID))

    await bot.send_message(CHAT_ID, f'❗️ Появился новый тикет #{id}!')
    await bot.send_message(CHAT_ID, f'📄 Тикет от <b>@{username} | CHAT_ID: {tg_id}</b>!\n\n{message}', message_thread_id=data.message_thread_id,parse_mode='html')

    return data.message_thread_id


@topic_router.message(F.chat.id == CHAT_ID)
async def send_message_from_topic(message: Message):
    data = await req.get_info_ticket(message.message_thread_id, 'topic')

    from run import bot
    if message.text:
        if message.text == '/close':
            await bot(EditForumTopic(chat_id=CHAT_ID, message_thread_id=message.message_thread_id, icon_custom_emoji_id=CLOSED_EMOJI_ID))
            await bot(CloseForumTopic(chat_id=CHAT_ID, message_thread_id=message.message_thread_id))
            await req.close_ticket(message.message_thread_id, 'topic')
            await bot.send_message(chat_id=data.get('from_id'), text=f'📄 <b>Ваш тикет #{data.get('id')}</b>\n\nБыл закрыт', parse_mode='HTML')
            await bot.send_message(chat_id=CHAT_ID, text=f'🔒 Вы закрыли тикет #{data.get('id')}', message_thread_id=message.message_thread_id, parse_mode='HTML')
        else:
            await bot.send_message(chat_id=data.get('from_id'), text=f'📄 <b>Ответ по тикету #{data.get('id')}</b>\n\n{message.text}\n\n<b>Ответьте на это сообщение свайпом влево.</b>', parse_mode='HTML')


@topic_router.message(F.reply_to_message)
async def send_message_from_bot(message: Message):
    try:
        data = await req.get_info_ticket(message.from_user.id, 'telegram')

        is_reply = bool(any(word in message.reply_to_message.text for word in ['тикет', 'ответ']))

        if is_reply:
            from run import bot
            if message.text:
                await bot.send_message(CHAT_ID, str(message.text), message_thread_id=data.get('topic'))
            elif message.video:
                await bot.send_video(chat_id=CHAT_ID, video=message.video.file_id, caption=message.text, message_thread_id=data.get('topic'))
            elif message.photo:
                await bot.send_photo(chat_id=CHAT_ID, photo=message.photo[-1].file_id, caption=message.text, message_thread_id=data.get('topic'))
    except AttributeError:
        await message.answer('🔒 Этот тикет уже закрыт!')




