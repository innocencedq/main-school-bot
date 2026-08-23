import pytz
import socket
from datetime import datetime
from aiogram.types import CallbackQuery, Chat

from app.components.logs.logs import logger
from app.components.keyboard import ScheduleKeyboards
from app.database.requests import create_user, get_image, is_user_exists, load_image, refresh_image


krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')


async def get_week():
    curr_time = datetime.now(krasnoyarsk_tz)
    day = curr_time.strftime('%A').lower()
    return day


async def get_fast_rasp(week: str):
    f = await get_image(week)
    day = week.split(':')[2]
    shift = week.split(':')[1]

    message = {
        "monday": "<b>🗓 Расписание на понедельник</b>\n\n❕ <i>Расписание только для 11-х и 9-х классов!</i>",
        "tuesday": "<b>🗓 Расписание на вторник</b>\n\n❕ <i>Расписание только для 11-х и 9-х классов!</i>",
        "wednesday": "<b>🗓 Расписание на среду</b>\n\n❕ <i>Расписание только для 11-х и 9-х классов!</i>",
        "thursday": "<b>🗓 Расписание на четверг</b>\n\n❕ <i>Расписание только для 11-х и 9-х классов!</i>",
        "friday": "<b>🗓 Расписание на пятницу</b>\n\n❕ <i>Расписание только для 11-х и 9-х классов!</i>"
    }
    markup = {
        "monday": ScheduleKeyboards.monday(shift=shift),
        "tuesday": ScheduleKeyboards.tuesday(shift=shift),
        "wednesday": ScheduleKeyboards.wednesday(shift=shift),
        "thursday": ScheduleKeyboards.thursday(shift=shift),
        "friday": ScheduleKeyboards.friday(shift=shift)
    }
    return f, message[day], markup[day]


def get_day_name(day: str) -> str:
    day_names = {
        "monday": "Понедельник",
        "tuesday": "Вторник", 
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница"
    }
    return day_names.get(day, day)

    
async def try_delete_msg_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass


async def loadschedule(method: str = 'firststart'):
    try:
        if method == 'firststart':
            week_days = ['schedule:1:monday', 'schedule:1:tuesday', 'schedule:1:wednesday', 'schedule:1:thursday', 'schedule:1:friday',
                        'schedule:2:monday', 'schedule:2:tuesday', 'schedule:2:wednesday', 'schedule:2:thursday', 'schedule:2:friday',
                        'schedule:calls']

            stub_id = await get_image(name='stub')

            for day in week_days:
                await load_image(img_id=stub_id, img_name=day)
        elif method == 'stubsload':
            week_days = ['schedule:1:monday', 'schedule:1:tuesday', 'schedule:1:wednesday', 'schedule:1:thursday', 'schedule:1:friday',
                        'schedule:2:monday', 'schedule:2:tuesday', 'schedule:2:wednesday', 'schedule:2:thursday', 'schedule:2:friday',]
            
            stub_id = await get_image(name='stub')

            for day in week_days:
                await refresh_image(img_id=stub_id, img_name=day)
        return '<b>Заглушки успешно загружены!</b>'
    except Exception as e:
        await logger.error(f'loadschedule: {e}')
        return '<b>Во время загрузки произошла ошибка... Необходимо заполнить залушки вручную</b>'
    

async def unauth_user_trap(user_id, username):
    if not await is_user_exists(user_id):
        await create_user(user_id, username)

        return 'Вы были восстановлены в базе данных, ваши настройки были сброшены по умолчанию!'


async def pagination(items, curr_id):
    """
    Returned:
        - next_id (int or None)
        - prev_id (int or None)
        - curr_idx (int)
    """
    index_dict = {index: value for index, value in enumerate(items)}
    
    next_idx = None
    prev_idx = None
    curr_idx = 0
    
    for index, value in index_dict.items():
        if value == int(curr_id):
            curr_idx = index
            
            if index == 0:
                prev_idx = None
                next_idx = 1 if len(index_dict) > 1 else None
            elif index == len(index_dict) - 1:
                prev_idx = index - 1
                next_idx = None
            else:
                prev_idx = index - 1
                next_idx = index + 1
            break

    if curr_idx == -1:
        return None, None, -1

    next_id = index_dict.get(next_idx)
    prev_id = index_dict.get(prev_idx)
    
    return prev_id, next_id, curr_idx


async def get_username_from_id(tg_id) -> str | None:
    from run import bot
    try:
        chat: Chat = await bot.get_chat(tg_id)
        return chat.username
    except Exception as e:
        await logger.error(f'get_username_from_id: {e}')
        return None


def get_server_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"