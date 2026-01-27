import os
import asyncio
import datetime
import pytz
from aiogram import Router, F
from datetime import datetime
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from sqlalchemy import select, update
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.components.diary.parsing import refresh_token as rf
from app.supportfunctions.main_utils import get_week, get_fast_rasp, loadschedule
from app.components.routers.callbacks import week_callback
from app.database.requests import add_admin, check_admin, get_all_users, get_full_info_user, get_list_admin, get_image, get_shift, load_image
from app.database.data import async_session, User, Images, Static
from app.components.keyboard import main_menu as keyboard_menu, ask_notify, ask_quick_menu
from app.components.keyboard import back_main_2 as back
from app.components.keyboard import for_vk_notify as kb_vk
from app.components.keyboard import notify as hide
from config import welcome_message, PATH_TO_IMAGES, ADMIN_KEY

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
        print(e)
        await message.answer('❌')



@router.message(Command('whoami'))
async def givemefromdatabase(message: Message):
    data = await get_full_info_user(message.from_user.id)

    id = data.get('id')
    tg_id = data.get('tg_id')
    username = data.get('username')
    date_started = data.get('date_started')
    notify_vk = data.get('notify_vk')
    quick_menu = data.get('quick_menu')
    requests_ai = data.get('requests_ai')
    refresh_token = data.get('refresh_token')
    access_token = data.get('access_token')
    shift = data.get('shift')
    extented_diary = data.get('extented_diary')
    tester = data.get('tester')
    notify_diary = data.get('notify_diary')
    is_admin = await check_admin(message.from_user.id)

    text = (f"👤 <b>{message.from_user.first_name}</b>\n\n"
            f"🧷 ID: <code>{id}</code>\n"
            f"🧷 Chat_ID: <code>{tg_id}</code>\n"
            f"🧷 Username: <code>{username}</code>\n"
            f"🧷 DateStump: <b>{date_started}</b>\n"
            f"🧷 Уведомления постов ВК: <b>{'Выключены' if notify_vk == 0 else 'Включены'}</b>\n"
            f"🧷 Быстрое меню: <b>{'Выключено' if quick_menu == 0 else 'Включено'}</b>\n"
            f"🧷 Запросы ИИ: <b>{requests_ai}</b>\n"
            f"🧷 refreshToken: <tg-spoiler>{refresh_token[:20]}</tg-spoiler>\n"
            f"🧷 accessToken: <tg-spoiler>{access_token[:20]}</tg-spoiler>\n"
            f"🧷 Выбранная смена: <b>{'Первая' if shift == 1 else 'Вторая'}</b>\n"
            f"🧷 Расширенный дневник: <b>{'Выключен' if extented_diary == 0 else 'Включен'}</b>\n"
            f"🧷 Права тестера: <b>{'Нету' if tester == 0 else 'Есть'}</b>\n"
            f"🧷 Уведомления дневника: <b>{'Выключены' if notify_diary == 0 else 'Включены'}</b>\n"
            f"🧷 Права доступа: <b>{'Пользователь' if not is_admin else 'Администратор'}</b>\n")



    await message.answer(text, parse_mode='html', reply_markup=hide)


@router.message(Command('getuser'))
async def get_user_info(message: Message):
    is_admin = await check_admin(message.from_user.id)
    
    if is_admin:
        arg = message.text.split(maxsplit=1)[1]

        if '@' in arg:
            username = arg[1:]
            data = await get_full_info_user(username, method='username')
            user = data.get('tg_id')
        else:
            user = arg
            data = await get_full_info_user(user)

        from run import bot
        user_ = await bot.get_chat(user)
        first_name = user_.first_name

        id = data.get('id')
        tg_id = data.get('tg_id')
        username = data.get('username')
        date_started = data.get('date_started')
        notify_vk = data.get('notify_vk')
        quick_menu = data.get('quick_menu')
        requests_ai = data.get('requests_ai')
        refresh_token = data.get('refresh_token')
        access_token = data.get('access_token')
        shift = data.get('shift')
        extented_diary = data.get('extented_diary')
        tester = data.get('tester')
        notify_diary = data.get('notify_diary')
        rights = await check_admin(user)

        text = (f"👤 <b>{first_name}</b>\n\n"
                f"🧷 ID: <code>{id}</code>\n"
                f"🧷 Chat_ID: <code>{tg_id}</code>\n"
                f"🧷 Username: <code>{username}</code>\n"
                f"🧷 DateStump: <b>{date_started}</b>\n"
                f"🧷 Уведомления постов ВК: <b>{'Выключены' if notify_vk == 0 else 'Включены'}</b>\n"
                f"🧷 Быстрое меню: <b>{'Выключено' if quick_menu == 0 else 'Включено'}</b>\n"
                f"🧷 Запросы ИИ: <b>{requests_ai}</b>\n"
                f"🧷 refreshToken: <tg-spoiler>{refresh_token[:20]}</tg-spoiler>\n"
                f"🧷 accessToken: <tg-spoiler>{access_token[:20]}</tg-spoiler>\n"
                f"🧷 Выбранная смена: <b>{'Первая' if shift == 1 else 'Вторая'}</b>\n"
                f"🧷 Расширенный дневник: <b>{'Выключен' if extented_diary == 0 else 'Включен'}</b>\n"
                f"🧷 Права тестера: <b>{'Нету' if tester == 0 else 'Есть'}</b>\n"
                f"🧷 Уведомления дневника: <b>{'Выключены' if notify_diary == 0 else 'Включены'}</b>\n"
                f"🧷 Права доступа: <b>{'Пользователь' if not rights else 'Администратор'}</b>\n")
        

        await message.answer(text, parse_mode='html', reply_markup=hide)
    else:
        await message.answer('❌ <b>У вас не хватает прав, чтобы воспользоваться этой командой!</b>\n\n❓ Если вы администратор, то воспользуйтесь командой <b>/givemeadm &lt;args&gt;</b>, где укажите суперключ <tg-spoiler>(находится в файле config.py)</tg-spoiler> или добавьте себя через базу данных.\nПример: /givemeadm 8bc6029e',
                             parse_mode='html')


    




@router.message(Command('thisfileidphoto'))
async def thisfileidphoto(message: Message):
    try:
        await message.answer(f'file_id: <code>{message.photo[-1].file_id}</code>', parse_mode='html')
    except Exception as e:
        print(e)
        await message.answer('❌')


@router.message(Command('thisfileid'))
async def thisfileid(message: Message):
    try:
        await message.answer(f'file_id: <code>{message.video.file_id}</code>', parse_mode='html')
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


@router.message(Command('loadimages'))
async def deeployimages(message: Message):
    is_admin = await check_admin(message.from_user.id)
    if is_admin:
        await message.answer(f'Начата загрузка изображений из <b>{PATH_TO_IMAGES}</b>!\n\n<b>Во время загрузки не удаляйте и не чистите чат с ботом!</b>', 
                            parse_mode='html')

        files = os.listdir(PATH_TO_IMAGES)
        len_files = len(files)
        curr = 0

        for filepath in files:
            image_name = filepath.split('.')[0]

            if image_name == 'calls':
                image_name = 'schedule:calls'

            curr += 1
            remaining = abs(len_files - curr)

            media = FSInputFile(PATH_TO_IMAGES + filepath)
            msg = await message.answer_photo(photo=media, 
                                            caption=f'<b>Остал{"ся" if remaining == 1 else "ось" if remaining in [0,2,3,4] or remaining % 10 in [0,2,3,4] else "ось"} <i>{remaining}</i> файл{"ов" if remaining % 10 in [0,5,6,7,8,9] or remaining % 100 in [11,12,13,14] else "а" if remaining % 10 in [2,3,4] else ""}</b>', 
                                            parse_mode='html')
            
            file_id = msg.photo[-1].file_id

            await load_image(file_id, image_name)
        
        await message.answer('<b>Переход к загрузке заглушек на расписание!</b>', parse_mode='html')

        res = await loadschedule()
        await message.answer(res)

        await message.answer('<b>Настройка изображений закончена!</b>\n\nТеперь можно удалить сообщения с изображениями или очистить чат с ботом.', 
                            parse_mode='html')
    else:
        await message.answer('❌ <b>У вас не хватает прав, чтобы воспользоваться этой командой!</b>\n\n❓ Если вы администратор, то воспользуйтесь командой <b>/givemeadm &lt;args&gt;</b>, где укажите суперключ <tg-spoiler>(находится в файле config.py)</tg-spoiler> или добавьте себя через базу данных.\nПример: /givemeadm 8bc6029e',
                             parse_mode='html')
        

@router.message(Command('givemeadm'))
async def givemeadm(message: Message):
    args = message.text.split(maxsplit=1)
    is_admin = await check_admin(message.from_user.id)

    if args[1] == ADMIN_KEY:
        if is_admin:
            await message.answer('<b>Вы уже являетесь администратором!</b>', parse_mode='html')
        else:
            await add_admin(message.from_user.id, message.from_user.username if message.from_user.username else 'unspecified_admin')
            await message.answer('<b>Вы были успешно добавлены в администраторы</b>\n\nДля проверки нажмите на команду -> /whoami', parse_mode='html')
    else:
        await message.answer('<b>Неверный ключ!</b>', parse_mode='html')


