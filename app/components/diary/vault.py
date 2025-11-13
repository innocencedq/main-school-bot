import asyncio

from app.database.data import User
from sqlalchemy import delete
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramForbiddenError
from datetime import datetime, timedelta

from app.supportfunctions.main_utils import krasnoyarsk_tz
from app.components.logs.logs import logger
from app.components.diary.response import get_marks_last_day
from app.database.data import async_session
from app.database import requests as req
from app.components.keyboard import notify as hide


async def notify_last_marks():
    while True:
        now = datetime.now(krasnoyarsk_tz)
        current_time = now.time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        target_shift = None
        if current_hour == 14 and current_minute == 0:
            target_shift = 1
        elif current_hour == 20 and current_minute == 0:
            target_shift = 2
        
        if target_shift is None:
            next_minute = now + timedelta(minutes=1)
            next_minute = next_minute.replace(second=0, microsecond=0)
            wait_seconds = (next_minute - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            continue
        
        users = await req.get_all_users_with_notify_mark()
        
        for user in users.get('users'):
            shift = await req.get_shift(user)
            
            if int(shift) != target_shift:
                continue
                
            marks_data = await get_marks_last_day(user)

            if marks_data.get('subjects_with_marks') == 0:
                continue
            
            response_text = "📙 <b>Оценки, полученные за последние сутки:</b>\n" + f"└<b> {marks_data.get('date_from')} — {marks_data.get('date_to')}</b>\n\n"

            counter = 1
            
            for subject in marks_data.get('subjects'):
                subject_text = f"{counter}. <b>{subject.get('subject')}.</b>\n"

                if subject.get('has_marks_last_24h'):
                    counter += 1

                    marks_lines = []
                    for mark in subject.get('marks'):
                        marks_str = ", ".join(mark.get('mark'))
                        marks_lines.append(f" <b>{marks_str}</b>")

                    subject_text += "└" + ",".join(marks_lines) + "\n"
                else:
                    continue

                response_text += subject_text

            try:
                from run import bot
                await bot.send_message(chat_id=user,
                                    text=response_text,
                                    reply_markup=hide,
                                    parse_mode="HTML")
            except TelegramForbiddenError:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == user))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{user} заблокировал бота!')
            except TelegramRetryAfter as e:
                retry_after = e.retry_after
                await asyncio.sleep(retry_after)
                continue
            except TelegramBadRequest:
                try:
                    async with async_session() as session:
                        stmt = (delete(User).where(User.tg_id == user))
                        await session.execute(stmt)
                        await session.commit()
                        await logger.info(f'{user} удалил аккаунт!')
                except Exception as e:
                    await logger.error(f"{e} /// in vault.py")
                    continue
            
            await asyncio.sleep(0.5)
        
        tomorrow = now + timedelta(days=1)
        next_run = krasnoyarsk_tz.localize(datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 14, 0, 0
        ))
        
        wait_seconds = (next_run - now).total_seconds()
        await logger.info(f"Notifying {target_shift} shift successfully done. Waiting {wait_seconds} seconds...")
        await asyncio.sleep(wait_seconds)

