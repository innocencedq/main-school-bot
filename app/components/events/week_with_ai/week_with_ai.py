from contextlib import suppress
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import update, func

from app.database.data import async_session, User
from app.components.events.week_with_ai.ai_generate import generate
from app.database.requests import get_requests_ai
from app.components.events.week_with_ai.keyboard_ai import kb_ai
from app.components.logs.logs import logger

week_with_ai = Router()


class AiWait(StatesGroup):
    msg = State()
    wait = State()


@week_with_ai.callback_query(F.data == 'week_ai')
async def week_ai_callback(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    request_count = await get_requests_ai(callback.message.chat.id)
    count_init = request_count[0]

    if count_init <= 0:
        await callback.message.answer("🤖 <b>Искусственный помощник</b>\n\nПривет! Если у тебя есть вопрос или нужна помощь — просто напиши, и я постараюсь помочь!\n\n<b>Жду твою задачу!</b> 🚀\n\n❕ <b>У вас закончились запросы</b> 😔", reply_markup=await kb_ai(), parse_mode='HTML')
    else:
        await callback.message.answer(f'🤖 <b>Искусственный помощник</b>\n\nПривет! Если у тебя есть вопрос или нужна помощь — просто напиши, и я постараюсь помочь!\n\n<b>Жду твою задачу!</b> 🚀\n\n<b>❕ Вы можете отправить еще {request_count[0]} {("запросов" if request_count[0] >= 5 else "запроса") if request_count[0] > 1 else "запрос"}</b>', reply_markup=await kb_ai(), parse_mode='HTML')
        await state.set_state(AiWait.msg)


@week_with_ai.message(AiWait.msg)
async def week_ai_message(message: Message, state: FSMContext):
    request_count = await get_requests_ai(message.chat.id)

    await message.answer('⏳ Подождите пожалуйста, ИИ начал отвечать на ваш запрос (~15 секунд) ')
    await state.set_state(AiWait.wait)

    with suppress(SyntaxWarning):
        text = await generate(message.text) + (f'\n\n*Искусственный помощник не запоминает контекст ваших сообщений\!*\n\n❕ *У вас осталось {request_count[0] - 1} {("запросов" if (request_count[0] - 1) >= 4 else "запроса") if (request_count[0] - 1) > 1 else "запрос"}*' if request_count[0] - 1 != 0 else f'\n\n❕ *У вас закончились запросы 😔*')

    try:
        await message.answer(text=text, reply_markup=await kb_ai(), parse_mode='MarkdownV2')
    except Exception:
        await message.answer(text=text + '\n\nОшибка форматирования', reply_markup=await kb_ai())
    await state.clear()

    async with async_session() as session:
        stmt = update(User).where(User.tg_id == message.chat.id).values(requests_ai = User.requests_ai - 1)
        await session.execute(stmt)
        await session.commit()

    await logger.info(
        f'Пользователь с id и username: {message.from_user.id} {message.from_user.username} отправил запрос: {message.text}')

    if (request_count[0] - 1) != 0:
        await state.set_state(AiWait.msg)


@week_with_ai.message(AiWait.wait)
async def week_ai_message(message: Message, state: FSMContext):
    await message.answer('⏳ Подождите пожалуйста, ИИ обратывает ваш запрос')