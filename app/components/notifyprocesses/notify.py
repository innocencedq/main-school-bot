import asyncio
from sqlalchemy import select, update, delete
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest

from app.database.data import async_session, User
from app.database.requests import get_all_users
from app.components.keyboard import notify, notify_schedule, notify_all_schedule, advert_notify_new
from app.components.logs.logs import logger


async def special_notify():
    for users in await get_all_users():
        try:
            from run import bot
            sent_msg = await bot.send_message(users, 'В связи с техническими проблемами БОТ ПЕРЕЕЗЖАЕТ -> @HelperSchool3bot', parse_mode='HTML',)
            await bot.pin_chat_message(users, sent_msg.message_id, disable_notification=False)
        except Exception as e:
            print(e)
            continue


async def new_advert_notify(title):
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users, f'⭕️ <b>Новое объявление!\n\n{title}</b>', parse_mode='HTML', reply_markup=await advert_notify_new())
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


async def new_advert_notify(title):
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users, f'‼️ <b>Изменение объявления!\n\n{title}</b>', parse_mode='HTML', reply_markup=await advert_notify_new())
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


async def notify_update_schedule():
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users, '<b>‼️ Обновление расписания!\n\n📅 Обновлено расписание на следующую неделю!</b>\n ᅠ ', parse_mode='html', reply_markup=await notify_all_schedule())
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



async def notify_update_calls():
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users,
                                   '<b>‼️ Обновление расписания!\n\n🔔 Обновлено расписание звонков!</b>\n ᅠ ',
                                   parse_mode='html', reply_markup=await notify_all_schedule())
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


async def notify_rework_schedule(message):
    for users in await get_all_users():
        days = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среду", "thursday": "четверг",
                "friday": "пятницу"}

        try:
            from run import bot
            await bot.send_message(users, f'<b>‼️ Обновление расписания!\n\n📅 Внесены изменения в расписании на {days[f"{message}"]}!</b>\n  ᅠ ', parse_mode='html', reply_markup=await notify_schedule(message))
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


async def technical_works():
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users, '<b>‼️ Технический перерыв!\n\n\n Бот будет вскоре отключен!</b>', parse_mode='html', reply_markup=notify)
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


async def technical_works_finish():
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users, '<b>‼️ Технический перерыв окончен!\n\n\n Бот включен! ✅</b>', parse_mode='html', reply_markup=notify)
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


async def message_admin(message):
    for users in await get_all_users():
        try:
            from run import bot
            await bot.send_message(users, f'{message}',parse_mode='HTML', reply_markup=notify)
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