from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import update

from app.components.routers.func_admin.keyboard_changer import ScheduleChangerKeyboard as kb_ch
from app.components.routers.func_admin.states_changer import FormChanger
from app.database.data import Images, async_session
from app.database.requests import del_image_from_redis
from app.components.keyboard import adm_back, confirm_day
from app.components.routers.admin import Form


router_adm = Router()

@router_adm.callback_query(F.data == "day_change")
async def day_change(callback: CallbackQuery):
    if callback.data == 'day_change':
        await callback.message.edit_text('<b>Внесение изменений в текущее расписание</b>\n\nВыберите в какую смену внести изменения.', 
                                         reply_markup=kb_ch.list_shift(method='day'), 
                                         parse_mode='html')
        

@router_adm.callback_query(F.data.in_(['week_first_shift:day', 'week_second_shift:day', 'week_first_shift:full', 'week_second_shift:full']))
async def choosed_shift(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'week_first_shift:day':
        await callback.message.edit_text('<b>Выберите день недели.</b>',
                                         reply_markup=kb_ch.week_changer(shift='1'),
                                         parse_mode='html')
        
    elif callback.data == 'week_second_shift:day':
        await callback.message.edit_text('<b>Выберите день недели.</b>',
                                         reply_markup=kb_ch.week_changer(shift='2'),
                                         parse_mode='html')
        
    elif callback.data == 'week_first_shift:full':
        await callback.message.edit_text('<b>Вы выбрали изменение полного расписания на 1 смену.</b>\n\nОтправьте сначало расписание на понедельник',
                                         reply_markup=adm_back,
                                         parse_mode='html')
        await state.update_data(current_shift="1")
        await state.set_state(Form.waiting_schedule)
        
    elif callback.data == 'week_second_shift:full':
        await callback.message.edit_text('<b>Вы выбрали изменение полного расписания на 2-у смену.</b>\n\nОтправьте сначало расписание на понедельник',
                                         reply_markup=adm_back,
                                         parse_mode='html')
        await state.update_data(current_shift="2")
        await state.set_state(Form.waiting_schedule)
        
        

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
    
    await callback.message.edit_caption('',
                                        reply_markup=None,
                                        parse_mode='html')

    async with async_session() as session:
        stmt = update(Images).where(Images.image_name == f'schedule:{shift}:{day}').values(image_id=file_id)
        await session.execute(stmt)
        await session.commit()
        await del_image_from_redis(f'schedule:{shift}:{day}')
    
    await callback.message.answer(f'<b>Расписание на {days[day]} загружено!</b>\n\nНе удаляйте отправленную фотографию! Оповестить всех?',
                                  reply_markup=confirm_day,
                                  parse_mode='html')