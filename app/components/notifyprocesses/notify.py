import asyncio
from sqlalchemy import delete
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest

from app.database.data import async_session, User
from app.database.requests import get_all_users
from app.components.keyboard import notify, notify_schedule, notify_all_schedule, advert_notify_new
from app.components.logs.logs import logger

async def new_advert_notify(title, msg):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        try:
            from run import bot
            await bot.send_message(users, f'⭕️ <b>Новое объявление!\n\n{title}</b>', parse_mode='HTML', reply_markup=await advert_notify_new())
            counter += 1
            await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue


async def notify_update_schedule(shift, msg):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        try:
            from run import bot
            await bot.send_message(users, f'<b>‼️ Обновление расписания!\n\n📅 Обновлено расписание на следующую неделю {"в <u>первую</u>" if shift == '1' else "во <u>вторую</u>"} смену!</b>\n ᅠ ', parse_mode='html', reply_markup=await notify_all_schedule())
            counter += 1
            await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue



async def notify_update_calls(msg):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        try:
            from run import bot
            await bot.send_message(users,
                                   '<b>‼️ Обновление расписания!\n\n🔔 Обновлено расписание звонков!</b>\n ᅠ ',
                                   parse_mode='html', reply_markup=await notify_all_schedule())
            counter += 1
            await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue


async def notify_rework_schedule(message, msg):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        days = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среду", "thursday": "четверг",
                "friday": "пятницу"}
        
        day = message.split(':')[2]
        shift = message.split(':')[1]

        try:
            from run import bot
            await bot.send_message(users, f'<b>‼️ Обновление расписания!\n\n📅 Внесены изменения в расписании на <u>{days[day]}</u> {"в <u>первую</u>" if shift == '1' else "во <u>вторую</u>"} смену!</b>\n  ᅠ ',
                                   parse_mode='html',
                                   reply_markup=await notify_schedule(message))
            counter += 1
            await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue


async def technical_works(msg):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        try:
            from run import bot
            await bot.send_message(users, '<b>‼️ Технический перерыв!\n\n\n Бот будет вскоре отключен!</b>', parse_mode='html', reply_markup=notify)
            counter += 1
            await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue


async def technical_works_finish(msg):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        try:
            from run import bot
            await bot.send_message(users, '<b>‼️ Технический перерыв окончен!\n\n\n Бот включен! ✅</b>', parse_mode='html', reply_markup=notify)
            counter += 1
            await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue


async def message_admin(message, msg = None):
    counter = 0
    user_list = await get_all_users()
    for users in user_list:
        try:
            from run import bot
            await bot.send_message(users, f'{message}',parse_mode='HTML', reply_markup=notify)
            counter += 1
            if msg:
                await bot.edit_message_text(text=f'⏳ Отправлено: {counter}/{len(user_list)}', message_id=msg.message_id, chat_id=msg.chat.id)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            continue
        except TelegramForbiddenError:
            async with async_session() as session:
                stmt = (delete(User).where(User.tg_id == users))
                await session.execute(stmt)
                await session.commit()
                await logger.info(f'{users} заблокировал бота!')
                continue
        except TelegramBadRequest:
            try:
                async with async_session() as session:
                    stmt = (delete(User).where(User.tg_id == users))
                    await session.execute(stmt)
                    await session.commit()
                    await logger.info(f'{users} удалил аккаунт!')
                    continue
            except Exception:
                continue