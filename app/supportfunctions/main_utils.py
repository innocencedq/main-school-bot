import pytz
from datetime import datetime
from aiogram.types import CallbackQuery


from app.components.keyboard import ScheduleKeyboards
from app.database.requests import create_user, get_image, is_user_exists, load_image


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
        "monday": "<b>🗓 Расписание на понедельник</b>",
        "tuesday": "<b>🗓 Расписание на вторник</b>",
        "wednesday": "<b>🗓 Расписание на среду</b>",
        "thursday": "<b>🗓 Расписание на четверг</b>",
        "friday": "<b>🗓 Расписание на пятницу</b>"
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
        elif method == 'stubsload':
            week_days = ['schedule:1:monday', 'schedule:1:tuesday', 'schedule:1:wednesday', 'schedule:1:thursday', 'schedule:1:friday',
                        'schedule:2:monday', 'schedule:2:tuesday', 'schedule:2:wednesday', 'schedule:2:thursday', 'schedule:2:friday',]

        stub_id = await get_image(week_name='stub')

        for day in week_days:
            await load_image(img_id=stub_id, img_name=day)

        return 'Successful intializing schedule images!'
    except Exception as e:
        return 'Failed initializing schedule images! Following initializing only in manual through database'
    

async def unauth_user_trap(user_id, username):
    if not await is_user_exists(user_id):
        await create_user(user_id, username)

        return 'Вы были восстановлены в базе данных, ваши настройки были сброшены поумолчанию!'