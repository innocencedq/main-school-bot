import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile, ReplyKeyboardRemove, Message
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import update, select

from app.components.keyboard import bug_report, advert_kb
from app.components.keyboard import ScheduleKeyboards
from app.components.keyboard import main_menu as menu_keyboard
from app.components.keyboard import settings_keyboard, back_main, notify
from app.components.keyboard import quick_menu_kb, ask_quick_menu, back_settings
import app.supportfunctions.main_utils as util
from app.database.requests import get_user_with_notify, get_all_users, get_image, get_quick_menu, get_tester, get_user_with_extended_diary, \
    get_all_data_about_advert, get_last_advert_id
from app.database.data import async_session, User, Static
import app.database.requests as req

from config import welcome_message, bug_report_message, DEVELOPER_ID

from app.components.routers.states import TechSup

router_callback = Router()

#Быстрая настройка
@router_callback.callback_query(F.data.in_(['yes_notify', 'no_notify']))
async def quick_settings_menu(callback: CallbackQuery):
    async with async_session() as session:
        if callback.data == 'yes_notify':
            stmt = (update(User).where(User.tg_id == callback.message.from_user.id).values(notify_vk=True))
            await session.execute(stmt)
            await session.commit()
    await callback.message.edit_text('⚙️ <b>Быстрая настройка</b>\n\nНужно ли быстрое меню?\n\n<a href="https://telegra.ph/Bystroe-menyu-04-09">Что такое быстрое меню</a>\n<b>Настройки можно будет изменить в главном меню</b>', parse_mode='HTML', reply_markup=ask_quick_menu)


#Расписание из главного меню
@router_callback.callback_query(F.data == 'rasp')
async def rasp_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    new_username = callback.from_user.username if callback.from_user.username else 'unspecific_user'
    async with async_session() as session:
        last_username = await session.scalar(select(User.username).where(User.tg_id == user_id))

        if last_username != new_username:
            stmt = update(User).where(User.tg_id == user_id).values(username = new_username)
            stmt2 = update(Static).where(Static.id == 1).values(active_users = Static.active_users + 1)
            await session.execute(stmt)
            await session.execute(stmt2)
            await session.commit()

    f = await get_image(week_name='main_rasp')
    photo = InputMediaPhoto(media=f, caption='<b>📅 Выберите день недели</b>', parse_mode='html')

    try:
        await callback.message.edit_media(media=photo, reply_markup=ScheduleKeyboards.rasp, parse_mode='html')
    except Exception:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await callback.message.answer('<b>📅 Выберите день недели</b>', reply_markup=ScheduleKeyboards.rasp, parse_mode='html')


#Назад в главное меню
@router_callback.callback_query(F.data.in_(['back', 'no_quick_menu']))
async def back_callback(callback: CallbackQuery, state: FSMContext, where: str = None):
    await state.clear()
    f = await get_image(week_name='main_menu')
    photo = InputMediaPhoto(media=f, caption=f"<b>Привет, {callback.from_user.first_name}! 👋</b>\n{welcome_message}\n\nДолго обрабатываются кнопки? ->\n/menu", parse_mode='html')
    if where == 'yes_quick_menu':
        await callback.message.answer_photo(photo=f, 
                                            caption=f"<b>Привет, {callback.from_user.first_name}! 👋</b>\n{welcome_message}\n\nДолго обрабатываются кнопки? ->\n/menu", 
                                            reply_markup=await menu_keyboard(user=callback.from_user.id), 
                                            parse_mode='html')
    else:
        await callback.message.edit_media(media=photo, caption=welcome_message, reply_markup=await menu_keyboard(user=callback.from_user.id), parse_mode='html')


#Настройки
@router_callback.callback_query(F.data == 'settings')
async def settings_callback(callback: CallbackQuery, where: str = None):
    async with async_session() as session:
        f = await get_image(week_name='main_settings')
        photo = InputMediaPhoto(media=f, caption='<b>⚙️ Настройки</b>\n\n <a href="https://telegra.ph/Bystroe-menyu-04-09">Что такое быстрое меню</a>', parse_mode='html')
        user = callback.from_user.id

        if user not in await get_all_users():
            username = callback.from_user.username if callback.from_user.username else "unspecific_user"
            new_user = User(
                tg_id=user,
                username=username,
            )
            session.add(new_user)
            await session.commit()


        if where == 'quick_menu':
            await callback.message.answer_photo(photo=f, caption='<b>⚙️ Настройки</b>\n\n <a href="https://telegra.ph/Bystroe-menyu-04-09">Что такое быстрое меню</a>', reply_markup=await settings_keyboard(user=user), parse_mode='html')
        else:
            await callback.message.edit_media(media=photo, reply_markup=await settings_keyboard(user=user))


#Измена настроек
@router_callback.callback_query(F.data == 'edit_settings')
async def edit_settings_callback(callback: CallbackQuery):
    async with async_session() as session:
        user = callback.from_user.id
        notify = await get_user_with_notify(user=user)

        if notify:
            stmt = (update(User).where(User.tg_id == user).values(notify_vk=False))
            await session.execute(stmt)
            await session.commit()
        else:
            stmt = (update(User).where(User.tg_id == user).values(notify_vk=True))
            await session.execute(stmt)
            await session.commit()

        await callback.answer('✅')
        await settings_callback(callback)


@router_callback.callback_query(F.data == 'edit_diary')
async def edit_diary(callback: CallbackQuery):
    user = callback.from_user.id
    flag = await get_user_with_extended_diary(user)

    async with async_session() as session:
        if flag:
            stmt = update(User).where(User.tg_id == user).values(extended_diary=False)
            await session.execute(stmt)
            await session.commit()
        else:
            stmt = update(User).where(User.tg_id == user).values(extended_diary=True)
            await session.execute(stmt)
            await session.commit()
        
        await callback.answer('✅')
        await settings_callback(callback)


@router_callback.callback_query(F.data.in_(['quick_menu', 'yes_quick_menu']))
async def quick_menu_callback(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        user = callback.from_user.id
        quick_menu = await get_quick_menu(user=user)

        if quick_menu:
            stmt = (update(User).where(User.tg_id == user).values(quick_menu=False))
            await session.execute(stmt)
            await session.commit()

            await callback.message.answer('🔄 Убираю быстрое меню...', reply_markup=ReplyKeyboardRemove())
            await asyncio.sleep(1)
            await callback.answer('✅ Быстрое меню успешно утилизировано!')
        else:
            stmt = (update(User).where(User.tg_id == user).values(quick_menu=True))
            await session.execute(stmt)
            await session.commit()

            await callback.message.answer('🔄 Развертываю быстрое меню...', reply_markup=quick_menu_kb)
            await asyncio.sleep(1)
            await callback.answer('✅ Быстрое меню готово к использованию!')

        if callback.data == "quick_menu":
            await settings_callback(callback, where='quick_menu')

        elif callback.data == "yes_quick_menu":
            await back_callback(callback, state, where='yes_quick_menu')

#Технический раздел
@router_callback.callback_query(F.data == 'bug_report')
async def bug_report_callback(callback: CallbackQuery):
    f = await get_image(week_name='settings_tech')
    photo = InputMediaPhoto(media=f, caption=bug_report_message, parse_mode='html')

    await callback.message.edit_media(media=photo, reply_markup=bug_report)

#Баг идея
@router_callback.callback_query(F.data.in_(['bug', 'idea']))
async def report_callback(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if callback.data == 'bug':
        await callback.message.answer('📄 <b>Тикет.</b>\n\nОпишите баг или идею.', reply_markup=back_settings, parse_mode='HTML')
        await state.set_state(TechSup.waiting_bug)

#Обработчики сообщений
@router_callback.message(TechSup.waiting_bug)
async def bug_message(message: Message, state: FSMContext):
    username = message.from_user.username if message.from_user.username else 'Неизвестный'
    msg = message.text

    try:
        await req.create_ticket(username, message.from_user.id, msg)
    except Exception as e:
        print(e)
        await message.answer('⚠️ Произошла непредвиденная ошибка. Попробуйте позже')

    data = await req.get_info_ticket(message.from_user.id, 'telegram')
    
    await message.answer(f'✅ <b>Тикет #{data['id']} был создан</b>\n\nОжидайте ответа', reply_markup=back_settings, parse_mode='HTML')
    await state.clear()



#Добавление тестера
@router_callback.callback_query(F.data == 'add_test')
async def add_test(callback: CallbackQuery):
    user = callback.from_user.id
    tester = await get_tester(user)
    async with async_session() as session:
        if tester:
            stmt = update(User).where(User.tg_id == user).values(tester = False)
            await session.execute(stmt)
            await session.commit()
            await callback.answer('Вы перестали быть тестером!')
        else:
            stmt = update(User).where(User.tg_id == user).values(tester = True)
            await session.execute(stmt)
            await session.commit()
            await callback.answer('Вы стали тестером!')


#Удаление по кнопке
@router_callback.callback_query(F.data == 'hide')
async def hide_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer('Вызовите /menu')


#Обработка страниц
@router_callback.callback_query(F.data == 'page')
async def page_callback(callback: CallbackQuery):
    await callback.answer('❌')
    pass


#Расписание
@router_callback.callback_query(F.data.in_(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'calls']))
async def week_callback(callback: CallbackQuery):
    day_data = {
        'monday': ('<b>🗓 Расписание на понедельник</b>', ScheduleKeyboards.monday),
        'tuesday': ('<b>🗓 Расписание на вторник</b>', ScheduleKeyboards.tuesday),
        'wednesday': ('<b>🗓 Расписание на среду</b>', ScheduleKeyboards.wednesday),
        'thursday': ('<b>🗓 Расписание на четверг</b>', ScheduleKeyboards.thursday),
        'friday': ('<b>🗓 Расписание на пятницу</b>', ScheduleKeyboards.friday),
        'calls': ('<b>🔔 Расписание звонков</b>', ScheduleKeyboards.calls)
    }
    
    if callback.data in day_data:
        caption, markup = day_data[callback.data]
        f = await get_image(week_name=callback.data)
        photo = InputMediaPhoto(media=f, caption=caption, parse_mode='html')
        await callback.message.edit_media(media=photo, reply_markup=markup)





@router_callback.callback_query(F.data.startswith('advert-'))
async def advert_callback(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        curr_advert_id = int(callback.data.split('-')[1])
        data = await get_all_data_about_advert(curr_advert_id)

        if data:
            title = data.get('title')
            description = data.get('description')
            image_id = data.get('image_id')
            date = str(data.get('date'))
            
            photo = InputMediaPhoto(media=str(image_id), 
                                    caption=f"<b>{str(title)}</b>\n\n{str(description)}\n\nДата создания: <b>{date.split(' ')[0]}</b>", 
                                    parse_mode='HTML')
            await callback.message.edit_media(media=photo, reply_markup=await advert_kb(curr_advert_id, callback.from_user.id))
        else:
            last_advert = await get_last_advert_id()
            data = await get_all_data_about_advert(last_advert)
            try:
                title = data.get('title')
                description = data.get('description')
                image_id = data.get('image_id')
                date = str(data.get('date'))
                
                photo = InputMediaPhoto(media=str(image_id), caption=f"<b>{str(title)}</b>\n\n{str(description)}\n\nДата создания: <b>{date.split(' ')[0]}</b>", parse_mode='HTML')
                await callback.message.edit_media(media=photo, reply_markup=await advert_kb(curr_advert_id, callback.from_user.id))
            except AttributeError:
                await callback.answer('Нет ни одного объявления...')

    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            print(e)
        else:
            await callback.answer('Вы уже в конце')



@router_callback.callback_query(F.data == 'help_with_schedule')
async def help_with_schedule(callback: CallbackQuery) -> None:
    await callback.message.answer(f'<b>⚠️ Неточности в расписании</b>\n\nВы можете помочь боту, скинув текущее расписание в личку <a href="https://t.me/HelperSchool3News">телеграмм канала</a> (слева снизу кнопка сообщения).\n\nНад расписанием второй смены ведутся работы, скоро обновим.', parse_mode='html', reply_markup=notify)
    await callback.answer('Удачно!')