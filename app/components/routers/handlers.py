import asyncio
import datetime
import pytz
from aiogram import Router, F
from datetime import datetime
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from sqlalchemy import select, update
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.components.diary.parsing import refresh_token as rf
from app.supportfunctions.main_utils import get_week, get_fast_rasp
from app.components.routers.callbacks import week_callback
from app.database.requests import get_all_users, get_list_admin, get_image, get_shift
from app.database.data import async_session, User, Images, Static
from app.components.keyboard import main_menu as keyboard_menu, ask_notify, ask_quick_menu
from app.components.keyboard import back_main_2 as back
from app.components.keyboard import for_vk_notify as kb_vk
from app.components.keyboard import notify as hide
from config import welcome_message

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        refresh_token = args[1]

        result = await rf(message.from_user.id, refresh_token)
        if result == 'success': 
            await message.answer('✅ Авторизация прошла успешно! Меню автоматически откроется через 1 секунду...')
            await asyncio.sleep(1)
        elif result == 'failed':
            await message.answer("❌ Ошибка на стороне КИАСУО, попробуйте позже. Меню автоматически откроется через 1 секунду...")
            await asyncio.sleep(1)


    if message.from_user.id in await get_all_users():
        await menu(message, state)
    else:
        async with async_session() as session:
            if message.from_user.id not in await get_all_users():
                username = message.from_user.username if message.from_user.username else "unspecific_user"
                new_user = User(
                             tg_id=message.from_user.id,
                             username=username,
                             )

                session.add(new_user)
                await session.commit()
        await quick_settings_notify(message=message)



async def quick_settings_notify(message: Message):
    await message.answer('⚙️ <b>Быстрая настройка</b>\n\nНужны ли вам уведомления о новых постах ВКонтакте?\n\n<b>Настройки можно изменить в главном меню</b>', parse_mode='HTML', reply_markup=ask_notify)


@router.message(Command('menu'))
async def menu(message: Message, state: FSMContext):
    try:
        await message.delete()
        await state.clear()
        f = await get_image(week_name='main_menu')
        await message.answer_photo(photo=f, caption=f"<b>Привет, {message.from_user.first_name}!</b> 👋\n{welcome_message}\n\nДолго обрабатываются кнопки? ->\n/menu", reply_markup=await keyboard_menu(message.from_user.id), parse_mode='html')
    except Exception as e:
        await message.answer('❌')



@router.message(Command('whoami'))
async def givemefromdatabase(message: Message):
    await message.answer(f'Ваш ID: <b>{message.from_user.id}</b>, Ваш USERNAME: <b>@{message.from_user.username}</b>', parse_mode='html')


@router.message(Command('thisfileidphoto'))
async def thisfileidphoto(message: Message):
    try:
        await message.answer(f'file_id: {message.photo[-1].file_id}')
    except Exception as e:
        print(e)
        await message.answer('❌')


@router.message(Command('thisfileid'))
async def thisfileid(message: Message):
    try:
        await message.answer(f'file_id: {message.video.file_id}')
    except Exception:
        await message.answer('❌')


@router.message(Command('getmychatid'))
async def getmychatid(message: Message):
    await message.answer(f'{message.from_user.id}')


@router.message(F.text == '🏠 Главное меню')
async def menu_text(message: Message, state: FSMContext):
    await menu(message=message, state=state)


@router.message(F.text == '🗓 Расписание на сегодня')
async def week_quick_callback(message: Message):
    user_id = message.from_user.id
    new_username = message.from_user.username if message.from_user.username else 'unspecific_user'
    async with async_session() as session:
        last_username = await session.scalar(select(User.username).where(User.tg_id == user_id))
        
        if last_username != new_username:
            stmt = update(User).where(User.tg_id == user_id).values(username = new_username)
            stmt2 = update(Static).where(Static.id == 1).values(active_users = Static.active_users + 1)
            await session.execute(stmt)
            await session.execute(stmt2)
            await session.commit()
    try:
        week = await get_week()
        shift = await get_shift(message.from_user.id)
        f, msg, markup = await get_fast_rasp(f"schedule:{shift}:{week}")

        await message.answer_photo(photo=f, caption=f'{msg}', reply_markup=markup, parse_mode='html')
    except Exception:
        await message.answer('😌 <b>Сегодня выходной!</b> Можешь спокойно отдыхать от школы)', parse_mode='html')


@router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('<b>Вы отменили все действия!</b>\n\nДля перехода в меню нажмите /menu', parse_mode='HTML')


@router.message(Command('newmenu'))
async def new_menu(message: Message, state: FSMContext):
    try:
        await message.delete()
        await state.clear()
        f = await get_image(week_name='main_menu')
        await message.answer_photo(photo=f, caption=f"<b>Привет, {message.from_user.first_name}!</b> 👋\n{welcome_message}\n\nДолго обрабатываются кнопки? ->\n/menu", reply_markup=await keyboard_menu(message.from_user.id), parse_mode='html')
    except Exception as e:
        await message.answer('❌')
