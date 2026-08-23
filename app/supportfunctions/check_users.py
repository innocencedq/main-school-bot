import asyncio
from aiogram.exceptions import TelegramForbiddenError

from app.database.requests import get_all_users, delete_user, get_full_info_user, edit_username
from app.supportfunctions.main_utils import get_username_from_id
from app.components.logs.logs import logger

async def remove_blocked_users():
    while True:
        try:
            all_users = await get_all_users()

            try:
                for user in all_users:
                    from run import bot
                    await bot.send_chat_action(user, 'typing')

                    username = await get_username_from_id(user)
                    await check_new_username(user, username)
                await asyncio.sleep(432000)
            except TelegramForbiddenError:
                await logger.info(f"{user} blocked bot!")
                await delete_user(user)
            except Exception:
                await logger.error("Unexcpected error in check_users.py // remove_blocked_users()")
        except Exception:
            await logger.error("Unexcpected error in check_users.py // remove_blocked_users()")
            await asyncio.sleep(3600)


async def check_new_username(telegram_id, username):
    user_info = await get_full_info_user(telegram_id)

    if user_info.get_data('username') != username:
        await edit_username(telegram_id, username)