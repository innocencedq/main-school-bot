import hashlib

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultCachedPhoto, InlineQueryResultArticle, InputTextMessageContent

import app.database.requests as req

from app.database.requests import get_image

router_inline_mode = Router()


@router_inline_mode.inline_query()
async def inline_inline_query(query: InlineQuery):
    text = query.query.lower()
    chat_id = query.from_user.id
    result_id: str = hashlib.md5(text.encode('utf-8')).hexdigest()
    shift_user = req.get_shift(chat_id)

    if text in ['понедельник', 'пн']:
        week_name = f'schedule:{shift_user}:monday'
        file_id = await get_image(week_name)

        result = InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=file_id,
            title="Расписание на понедельник",
            description="Нажмите, чтобы отправить расписание на понедельник",
            caption="📆 <b>Расписание на понедельник</b>",
            parse_mode='HTML'
        )

        await query.answer(results=[result], cache_time=1, is_personal=True)

    elif text in ['вторник', 'вт']:
        week_name = f'schedule:{shift_user}:tuesday'
        file_id = await get_image(week_name)

        result = InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=file_id,
            title="Расписание на вторник",
            description="Нажмите, чтобы отправить расписание на вторник",
            caption="📆 <b>Расписание на вторник</b>",
            parse_mode='HTML'
        )

        await query.answer(results=[result], cache_time=1, is_personal=True)

    elif text in ['среда', 'ср']:
        week_name = f'schedule:{shift_user}:wednesday'
        file_id = await get_image(week_name)

        result = InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=file_id,
            title="Расписание на среду",
            description="Нажмите, чтобы отправить расписание на среду",
            caption="📆 <b>Расписание на среду</b>\n\n‼️ Расписание <i>пятых, шестых, седьмых, восьмых, десятых и одиннадцатых классов</i> перенесены во вторую смену!\n‼️ Расписание <i>первых, вторых, третьих и четвертых классов</i> перенесены в первую смену!",
            parse_mode='HTML'
        )

        await query.answer(results=[result], cache_time=1, is_personal=True)

    elif text in ['четверг', 'чт']:
        week_name = f'schedule:{shift_user}:thrusday'
        file_id = await get_image(week_name)

        result = InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=file_id,
            title="Расписание на четверг",
            description="Нажмите, чтобы отправить расписание на четверг",
            caption="📆 <b>Расписание на четверг</b>",
            parse_mode='HTML'
        )

        await query.answer(results=[result], cache_time=1, is_personal=True)

    elif text in ['пятница', 'пт']:
        week_name = f'schedule:{shift_user}:friday'
        file_id = await get_image(week_name)

        result = InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=file_id,
            title="Расписание на пятницу",
            description="Нажмите, чтобы отправить расписание на пятницу",
            caption="📆 <b>Расписание на пятницу</b>",
            parse_mode = 'HTML'
        )

        await query.answer(results=[result], cache_time=1, is_personal=True)

    elif text in ['звонки', 'зв', 'zv']:
        week_name = f'schedule:calls'
        file_id = await get_image(week_name)

        result = InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=file_id,
            title="Расписание звонков",
            description="Нажмите, чтобы отправить расписание звонков",
            caption="🔔 <b>Расписание звонков</b>",
            parse_mode = 'HTML'
        )

        await query.answer(results=[result], cache_time=1, is_personal=True)
    else:
        result = InlineQueryResultArticle(
            id=result_id,
            title='Введите день недели',
            input_message_content=InputTextMessageContent(message_text='❌')
        )
        await query.answer(results=[result], cache_time=1, is_personal=True)
