from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import update, func

from app.components.logs.logs import logger
from app.database.data import User, async_session
from app.components.events.events_keyboard import woman_day_keyboard, woman_day_start, are_u_sure, report
from app.components.keyboard import back_main, notify
from app.database.requests import get_list_username, get_username_with_id, get_user_value_valentines, get_user_value_valentines_from_top

router_woman_day = Router()


char_replace = {
    'а': ['а', 'a', '@'],
    'б': ['б', '6', 'b'],
    'в': ['в', 'b', 'v'],
    'г': ['г', 'r', 'g'],
    'д': ['д', 'd'],
    'е': ['е', 'e'],
    'ё': ['ё', 'e'],
    'ж': ['ж', 'zh', '*'],
    'з': ['з', '3', 'z'],
    'и': ['и', 'u', 'i'],
    'й': ['й', 'u', 'i'],
    'к': ['к', 'k', 'i{', '|{'],
    'л': ['л', 'l', 'ji'],
    'м': ['м', 'm'],
    'н': ['н', 'h', 'n'],
    'о': ['о', 'o', '0'],
    'п': ['п', 'n', 'p'],
    'р': ['р', 'r', 'p'],
    'с': ['с', 'c', 's'],
    'т': ['т', 'm', 't'],
    'у': ['у', 'y', 'u'],
    'ф': ['ф', 'f'],
    'х': ['х', 'x', 'h', '}{'],
    'ц': ['ц', 'c', 'u,'],
    'ч': ['ч', 'ch'],
    'ш': ['ш', 'sh'],
    'щ': ['щ', 'sch'],
    'ь': ['ь', 'b'],
    'ы': ['ы', 'bi'],
    'ъ': ['ъ'],
    'э': ['э', 'e'],
    'ю': ['ю', 'io'],
    'я': ['я', 'ya']
}


bad_words = []


def create_normalizer():
    reverse_char_replace = {}

    for original_char, replacements in char_replace.items():
        for replacement in replacements:
            reverse_char_replace[replacement] = original_char

    def normalize_text(text: str) -> str:
        return ''.join(reverse_char_replace.get(char, char) for char in text.lower())

    return normalize_text


normalize_text = create_normalizer()


async def contain_bad_words(text: str, bad_words: set) -> bool:
    normalized_text = normalize_text(text)
    return any(word in normalized_text for word in bad_words)


class Form(StatesGroup):
    username = State()
    message = State()


@router_woman_day.callback_query(F.data == 'woman_day_menu')
async def callback_woman_day_menu(callback: CallbackQuery,state: FSMContext):
    value = await get_user_value_valentines(callback.from_user.id)
    getting_value = await get_user_value_valentines_from_top(callback.from_user.id)

    if value[0] == 0:
        await callback.message.edit_text(
            f'<b>🌸 День женщин</b>\n\nОтправляйте и принимайте анонимные поздравления от других пользователей бота!\n\n<b>Чтобы начать отправку поздравления, нажмите на кнопку <u>Начать</u></b>\n\n◽️ <b>Вам отправили {getting_value[0]} поздравлений</b>\n\n❕ <b>У вас закончились поздравления!</b>',
            reply_markup=woman_day_keyboard, parse_mode='HTML')
    else:
        await callback.message.edit_text(f'<b>🌸 День женщин</b>\n\nОтправляйте и принимайте анонимные поздравления от других пользователей бота!\n\n<b>Чтобы начать отправку поздравления, нажмите на кнопку <u>Начать</u></b>\n\n◽️ <b>Вам отправили {getting_value[0]} поздравлений</b>\n\n❕ <b>Вы еще можете отправить <u>{value[0]}</u> поздравлений!</b>', reply_markup=woman_day_keyboard, parse_mode='HTML')
    await state.clear()


@router_woman_day.callback_query(F.data == 'woman_day')
async def callback_woman_day(callback: CallbackQuery, state: FSMContext):
    value = await get_user_value_valentines(callback.from_user.id)

    if value[0] != 0:
        await callback.message.edit_text('Отправьте мне имя пользователя (юзернейм), которому хотите отправить поздравление', reply_markup=woman_day_start)
        await state.set_state(Form.username)
    else:
        await callback.message.edit_text('❌ <b>У вас кончились поздравления!</b>', reply_markup=woman_day_start, parse_mode='HTML')


@router_woman_day.message(Form.username)
async def callback_username(message: Message, state: FSMContext):
    username = message.text.lstrip('@')

    users = await get_list_username(username)

    if username == message.from_user.username or username == 'unspecific_user':
        await message.answer('Вы не можете отправить поздравление самому себе!')
    else:
        if users:
            user = users[0]

            await message.answer(f'Вы выбрали @{user}, а теперь введите свой текст с поздравлением', reply_markup=woman_day_start)

            await state.update_data(username=user)
            await state.set_state(Form.message)
        else:
            await message.answer('Вы ввели неверное имя пользователя, либо его не задали или пользователь не использует бота!')


@router_woman_day.message(Form.message)
async def callback_message(message: Message, state: FSMContext):
    data = await state.get_data()

    username = data.get('username')
    await state.update_data(username=username, message=message.text)

    if not message.text:
        await message.answer('Можно отправлять только текст и эмодзи!')
    else:
        if await contain_bad_words(text=message.text, bad_words=bad_words):
            await message.answer('Ваше сообщение содержит недопустимые слова! Пожалуйста, измените текст.')
        else:
            await message.answer(f'<b>📝 Вы отправите поздравление @{username} со следующим содержанием:</b>\n\n{message.text}\n\n<b>Для изменения текста, отправьте новое сообщение\nВы уверены?</b>', reply_markup=are_u_sure, parse_mode='html')


@router_woman_day.callback_query(F.data == 'yes_valentine')
async def callback_yes_valentine(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    username = data.get('username')
    message = data.get('message')

    async with async_session() as session:
        for chat_id in await get_username_with_id(username=username):
            try:
                from run import bot
                await bot.send_message(chat_id, f'🎉 <b>Вам отправили поздравление!</b>\n\n{message}', reply_markup=report, parse_mode='html')
                await state.clear()

                await callback.message.edit_text('<b>✅ Поздравление отправлено!</b>', reply_markup=woman_day_start, parse_mode='html')
                await logger.info(f'Пользователь с id и username: {callback.from_user.id} {callback.from_user.username} отправил сообщение: \n<{message}>,\n пользователю с именем: @{username}')

                stmt = (update(User).where(User.tg_id == chat_id).values(valentines_top = User.valentines_top + 1))
                await session.execute(stmt)

                stmt2 = (update(User).where(User.tg_id == callback.from_user.id, User.valentines_value > 0).values(valentines_value = User.valentines_value - 1))
                await session.execute(stmt2)

                await session.commit()
            except Exception:
                await message.edit_text('❌ <b>Не удалось отправить поздравление, возможно пользователь заблокировал бота! Попробуйте еще раз.</b>', reply_markup=woman_day_start, parse_mode='html')


@router_woman_day.callback_query(F.data == 'reporting')
async def callback_reporting(callback: CallbackQuery):
    await callback.message.answer('⛔️ <b>Жалоба</b>\n\nПересылайте сообщение с оскорбительным поздравлением мне -> @wh47chu54y\n\nᅠ ᅠ ', reply_markup=notify, parse_mode='html')