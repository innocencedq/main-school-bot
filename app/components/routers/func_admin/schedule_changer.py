from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Chat, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.formatting import Italic, Bold, Text, Underline, Url, BlockQuote, Spoiler, Code, ExpandableBlockQuote, TextLink, Strikethrough
from aiogram.utils.text_decorations import html_decoration as hd
from sqlalchemy import update

from app.components.routers.func_admin.keyboard_changer import ScheduleChangerKeyboard as kb_ch
from app.components.routers.func_admin.states_changer import FormChanger
from app.components.routers.callbacks import back_callback
from app.database.data import Images, async_session, Admin
from app.database.requests import count_users, check_admin, advert_write_sql, refresh_last_advert_id, del_image_from_redis, get_all_data_about_advert, update_data_about_advert, \
    deleting_data_about_advert, refresh_last_advert_id, get_image, add_admin, zaglushka_deploy
from app.components.keyboard import adm_back, confirm_day
from app.components.keyboard import notify as hide
from app.components.notifyprocesses.notify import notify_update_schedule, technical_works, technical_works_finish, notify_rework_schedule, message_admin, notify_update_calls, \
    new_advert_notify


router_adm = Router()

@router_adm.callback_query(F.data == "day_change")
async def day_change(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'day_change':
        await callback.message.edit_text('<b>Внесение изменений в текущее расписание</b>\n\nВыберите в какую смену внести изменения.', 
                                         reply_markup=kb_ch.list_shift, 
                                         parse_mode='html')
        

@router_adm.callback_query(F.data.in_(['week_first_shift', 'week_second_shift']))
async def choosed_shift(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'week_first_shift':
        await callback.message.edit_text('<b>Выберите день недели.</b>',
                                         reply_markup=kb_ch.week_changer(shift='1'),
                                         parse_mode='html')
    elif callback.data == 'week_second_shift':
        await callback.message.edit_text('<b>Выберите день недели.</b>',
                                         reply_markup=kb_ch.week_changer(shift='2'),
                                         parse_mode='html')
        

@router_adm.callback_query(F.data.startswith('changer:'))
async def select_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split(':')[1]
    shift = callback.data.split(':')[2]
    days = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среду", "thursday": "четверг", "friday": "пятницу"}

    await callback.message.edit_text(f'Отправьте новое расписание на {days[day]}',
                                     reply_markup=adm_back,
                                     parse_mode='html')

    await state.update_data(day=day, shift=shift)
    await state.set_state(FormChanger.waiting_day)


@router_adm.message(FormChanger.waiting_day)
async def change_day(message: Message, state: FSMContext):
    try:
        days = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среду", "thursday": "четверг", "friday": "пятницу"}
        data = await state.get_data()

        day = data.get('day')
        shift = data.get('shift')
        file_id = message.photo[0].file_id

        await state.update_data({f'file_id': file_id})
        await message.answer_photo(photo=file_id,
                                   caption=f"Подтвердите изменение расписания на {days[day]} в {shift} смену",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [InlineKeyboardButton(text='Продолжить', callback_data='agree')],
                                       [InlineKeyboardButton(text='Отмена', callback_data='adminpanel')]
                                   ]))
    except Exception as e:
        print(e)
        await message.answer('Что-то пошло не так... Перезайдите в админ панель и попробуйте снова - /adminpanel')


@router_adm.callback_query(F.data == 'agree')
async def agreed(callback: CallbackQuery, state: FSMContext):
    days = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среду", "thursday": "четверг", "friday": "пятницу"}
    data = await state.get_data()
    day = data.get('day')
    shift = data.get('shift')
    file_id = data.get('file_id')

    async with async_session() as session:
        stmt = update(Images).where(Images.image_name == f'schedule:{shift}:{day}').values(image_id=file_id)
        await session.execute(stmt)
        await session.commit()
        await del_image_from_redis(f'schedule:{shift}:{day}')
    
    await callback.message.answer(f'Расписание на {days[day]} загружено! Не удаляйте отправленную фотографию! Оповестить всех?', reply_markup=confirm_day)