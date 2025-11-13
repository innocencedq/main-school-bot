from datetime import datetime, timedelta

from app.components.diary.parsing import refresh_token
from sqlalchemy import update
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaVideo, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest

from app.components.logs.logs import logger
from app.database.data import User, async_session
from app.components.diary.response import get_all_period_marks as all_marks
from app.components.diary.response import get_homework as gh
from app.components.diary.response import get_marks_last_5_days as get_marks
from app.components.keyboard import diary_settings_kb, main_diary_kb, back_to_diary, methods_auth, notify, choose_marks, escape_from_marks
from app.database.requests import get_image, get_user_with_notify_mark


callback_diary = Router()


@callback_diary.callback_query(F.data == 'main_diary')
async def main_diary(callback: CallbackQuery):
    f = await get_image(week_name='diary')
    photo = InputMediaPhoto(media=f, caption='<b>📔 Дневник</b>\n\n', parse_mode='html')
    await callback.message.edit_media(photo, reply_markup=await main_diary_kb(callback.from_user.id))


@callback_diary.callback_query(F.data == 'marks')
async def marks(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.message.answer('🗓 За какой период просмотреть оценки?', reply_markup=choose_marks)


@callback_diary.callback_query(F.data.in_(['auth_android_chrome', 'auth_ios_safari', 'auth_pc']))
async def auth_android_chrome(callback: CallbackQuery):
    if callback.data == 'auth_android_chrome':
        # file_id = await get_image('guide_android')
        auth_android = "📱 <b>Вход через Android (Chrome)</b>\n\n" \
                    """1️⃣ <b>Шаг 1:</b> Скопируйте код, после чего перейдите на сайт КИАСУО и авторизуйтесь любым удобным способом <a href="https://pwa.kiasuo.ru/schedule">pwa.kiasuo.ru</a>\n""" \
                    """<pre>javascript:(() => { const a = (JSON.parse(localStorage.getItem("auth-store") || "{}"))?.refreshToken; if (a) { window.location.href = `https://t.me/HelperSchool3bot?start=${a}`; } })();</pre>\n""" \
                    "2️⃣ <b>Шаг 2:</b> Нажмите на три точки в правом верхнем углу, в появившимся окне, нажмите на звездочку, после, снизу появиться плашка, нажмите на синий текст <b>«Изменить»</b>\n" \
                    "3️⃣ <b>Шаг 3</b>: В появившимся окне, измените первую строку (название) на «<code>Школьный помощник</code>» (кликабельно), а вторую (URL) на скопированный код и выйдите, нажав на кнопку назад\n" \
                    "4️⃣ <b>Шаг 4</b>: В поисковой строке на сайте введите «<b>Школьный помощник</b>» и нажмите на предложение со значком звезды\n\n" \
                    "⁉️ Если потребуется обновить сессию, то <b>закладку можно использовать повторно.\n\n</b>" \
                    "Если вы можете записать видеоинструкцую, то отпишите в <b>Настройки -> Технический раздел -> Тикет</b>. (видео сразу скидывать не нужно)\n" 
        # video = InputMediaVideo(media=file_id, caption=auth_android, parse_mode='HTML')
        await callback.message.edit_caption(caption=auth_android, reply_markup=back_to_diary, parse_mode='HTML')
    elif callback.data == 'auth_ios_safari':
        # file_id = await get_image('guide_ios')
        auth_ios = "📱 <b>Вход через iOS (Safari)</b>\n\n" \
                    """1️⃣ <b>Шаг 1:</b> Скопируйте код из отдельного сообщения, после чего перейдите на сайт КИАСУО и авторизуйтесь любым удобным способом <a href="https://pwa.kiasuo.ru/schedule">pwa.kiasuo.ru</a> (при открытии cсылки через телеграм, нажмите на кнопку «<b>Открыть в Safari</b>» в правом углу)\n""" \
                    "2️⃣ <b>Шаг 2:</b> Нажмите снизу на треугольник со стреллочкой вверх (iOS 18), в открывшемся меню выберите «<b>Добавить в избранное</b>», сохраните, после нажмите снизу на открытую книжку, после открытия меню зажмите закладку «<b>Дневник</b>», после зажатия, пролистав ниже, нажмите на «<b>Изменить</b>»\n" \
                    "3️⃣ <b>Шаг 3</b>: Измените первую строку (название) на «<code>Школьный помощник</code>» (кликабельно), а вторую (URL) на скопированный код\n" \
                    "4️⃣ <b>Шаг 4</b>: Снова нажмите снизу на открытую книжку, после чего нажмите один раз на «<b>Школьный помощник</b>»\n\n" \
                    "⁉️ Если потребуется обновить сессию, то <b>закладку можно использовать повторно.\n\n</b>" \
                    "Если вы можете записать видеоинструкцую, то отпишите в <b>Настройки -> Технический раздел -> Тикет</b>. (видео сразу скидывать не нужно)\n" 
        # video = InputMediaVideo(media=file_id, caption=auth_ios, parse_mode='HTML')
        await callback.message.edit_caption(caption=auth_ios, parse_mode='HTML', reply_markup=notify)
        await callback.message.answer("""javascript:(() => { const a = (JSON.parse(localStorage.getItem("auth-store") || "{}"))?.refreshToken; if (a) { window.location.href = `https://t.me/HelperSchool3bot?start=${a}`; } })();""", reply_markup=back_to_diary)
    elif callback.data == 'auth_pc':
        file_id = await get_image('guide_pc')
        auth_pc = "💻 <b>Вход через ПК</b>\n\n" \
                    """1️⃣ <b>Шаг 1:</b> Скопируйте код, после чего перейдите на сайт КИАСУО и авторизуйтесь <a href="https://pwa.kiasuo.ru/schedule">pwa.kiasuo.ru</a>\n""" \
                    """<pre>(() => { const a = (JSON.parse(localStorage.getItem("auth-store") || "{}"))?.refreshToken; if (a) { window.location.href = `https://t.me/HelperSchool3bot?start=${a}`; } })();</pre>\n""" \
                    "2️⃣ <b>Шаг 2:</b> Зайдите в панель разработчика и разрешите вставку в консоль (ПКМ -> Исследовать код -> Console (Консоль) -> в консоли allow pasting)\n" \
                    "3️⃣ <b>Шаг 3</b>: Вставьте скопированный код в консоль и нажмите Enter\n" \
                    "4️⃣ <b>Шаг 4</b>: После перезагрузки страницы у Вас появиться маленькое окно, нажмите 'Открыть с помощью Telegram'\n\n" \
                    "<b>Пошаговое выполнение показано в видеоинструкции</b>\n\n" \
                    "⁉️ <b>На стороне сервера храниться лишь Ваш refreshToken и accessToken, позволяющие брать данные оценок!</b>"
        video = InputMediaVideo(media=file_id, caption=auth_pc, parse_mode='HTML')
        await callback.message.edit_media(media=video, reply_markup=back_to_diary, parse_mode='HTML')
        

@callback_diary.callback_query(F.data == 'get_homework')
async def get_homework(callback: CallbackQuery):
    try:
        await callback.message.edit_caption(caption='⏳ Подождите, загружаю домашние задания… (~5 секунд)',
                                            reply_markup=None)

        today = datetime.now()
        homework_data = await gh(callback.from_user.id)
        response_text = (
            "<b>📖 Заданные домашние задания</b>\n\n"
        )
        number = 0

        for subjects in homework_data['subjects']:
            subject = subjects['subject']

            homework_text = None
            homework_check_at = None
            for homework in subjects['homework']:
                if 'text' in homework:
                    homework_text = homework['text']
                    homework_check_at = homework['check_at']

            subject_text = ()
            if homework_check_at:
                format_date = datetime.strptime(homework_check_at, "%Y-%m-%d") 
                if format_date.date() >= today.date(): 
                    split_date = {
                        "monday": "пн",
                        "tuesday": "вт",
                        "wednesday": "ср",
                        "thursday": "чт",
                        "friday": "пт"
                    }
                    if homework_text not in response_text:
                        number += 1
                        subject_text = (
                            f"<b>{number}. {subject}</b>\n"
                            f"├ <code>{homework_text}</code>\n"
                            f"└ Проверка <b>{format_date.strftime('%d.%m')} ({'сегодня' if format_date == today else split_date[format_date.strftime('%A').lower()]})</b>\n\n"
                        )

            response_text += subject_text if subject_text else ""
        
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await callback.message.answer(text=response_text + "\n<b>Обращай внимание на дату проверки!</b>",
                                      parse_mode='HTML',
                                      reply_markup=back_to_diary)
    except TelegramBadRequest as e:
            await callback.message.answer('⚠️ Обновите меню! /menu')
    except Exception as e:
        print(e)
        await callback.message.answer(text="⚠️ Произошла ошибка при получении домашнего задания. Попробуйте обновить сессию.", reply_markup=back_to_diary)


@callback_diary.callback_query(F.data == 'check_marks')
async def marks_last_5_days(callback: CallbackQuery):
    try:
        await callback.message.edit_text('⏳ Подождите, загружаю оценки… (~5 секунд)')
        marks_data = await get_marks(callback.from_user.id)
        
        response_text = (
            f"📊 <b>Успеваемость за последние 5 дней</b>\n"
            f"📅 {marks_data['date_from']} - {marks_data['date_to']}\n\n"
        )
        

        for subject in marks_data['subjects']:
            subject_text = (
                f"<b>{subject['number']}. {subject['subject']}</b>\n"
                f"├ Средний балл: <b>{subject['average_mark'] or '—'}</b> <b>{subject['average_status']}</b>\n"
            )
            
            if subject['has_marks_last_5_days']:
                marks_lines = []
                for day in subject['marks']:
                    marks_str = ", ".join(day['mark'])
                    marks_lines.append(f"│  <b>{day['date']}: {marks_str}</b>")
                
                subject_text += "├ Последние оценки:\n" + "\n".join(marks_lines) + "\n"
            else:
                subject_text += f"└ Нет оценок за 5 дней\n"
            
            response_text += subject_text + "\n"
        
        await callback.message.edit_text(text=response_text, reply_markup=escape_from_marks, parse_mode="HTML")
    
    except TelegramBadRequest:
            await callback.message.answer('⚠️ Обновите меню! /menu')
    except Exception as e:
        print(e)
        await callback.message.edit_text(text="⚠️ Произошла ошибка при получении оценок. Попробуйте обновить сессию.", reply_markup=back_to_diary)


@callback_diary.callback_query(F.data == 'get_all_marks')
async def get_all_period_marks(callback: CallbackQuery):
    try:
        await callback.message.edit_text('⏳ Подождите, загружаю оценки… (~5 секунд)')
        marks_data = await all_marks(callback.from_user.id)

        response_text = "📊 <b>Успеваемость за текущую четверть/полугодие</b>\n\n"
        
        total_marks = 0
        excellent_subjects = 0
        good_subjects = 0
        bad_subjects = 0

        for subject in marks_data['subjects']:
            if subject['rounded_mark'] == 5:
                excellent_subjects += 1
            elif subject['rounded_mark'] == 4:
                good_subjects += 1
            elif subject['rounded_mark'] in (2, 3):
                bad_subjects += 1
            
            subject_text = (
                f"<b>{subject['number']}. {subject['subject']}</b>\n"
                f"├ Средний балл: <b>{subject['average_mark'] or '—'}</b> <b>{subject['average_status']}</b>\n"
            )
            
            if subject['has_marks']:
                marks_lines = []
                for day in subject['marks']:
                    marks_str = ", ".join(day['marks'])
                    total_marks += len(day['marks'])
                    marks_lines.append(f"└  <b>{marks_str}</b>")
                
                subject_text += "├ Последние оценки:\n" + "\n".join(marks_lines) + "\n"
            else:
                subject_text += f"└ Нет оценок\n"

            response_text += subject_text + "\n"
        
        if total_marks == 0:
            response_text += (
                f"<b>📈 Краткий свод оценок:</b>\n"
                f"• Вы еще не получили оценок.\n\n"
            )
        else:
            response_text += (
                f"<b>📈 Краткий свод оценок:</b>\n"
                f"• Получено оценок: {total_marks}\n"
                f"• Отличных предметов (5): {excellent_subjects}\n"
                f"• Хороших предметов (4): {good_subjects}\n"
                f"• Проблемных предметов (2-3): {bad_subjects}\n\n"
            )
        
        
        await callback.message.edit_text(text=response_text, reply_markup=escape_from_marks, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "MESSAGE_TOO_LONG" in str(e):
            await callback.message.answer('⚠️ <b>Вы получили слишком много оценок...</b>\n\nВы не можете просматривать оцеки за полугодие/четверть из-за большого количества оценок (ограничение телеграмма)\n\n/menu',
                                          parse_mode='html')
        else:
            await callback.message.answer('⚠️ <b>Обновите меню!</b>\n\n/menu',
                                          parse_mode='html')
    except Exception as e:
        await callback.message.edit_text(text="⚠️ Произошла ошибка при получении оценок. Попробуйте обновить сессию.", reply_markup=back_to_diary)


@callback_diary.callback_query(F.data == 'methods_auth')
async def methods(callback: CallbackQuery):
    await callback.message.edit_caption(caption='✍️ <b>Обновление токенов вручную</b>\n\nВыберите удобный способ',
                                        reply_markup=methods_auth,
                                        parse_mode='html')


@callback_diary.callback_query(F.data == 'settings_diary')
async def settings_diary(callback: CallbackQuery):
    try:
        await callback.message.edit_caption(caption='⚙️ <b>Настройки дневника</b>\n\n<a href="https://telegra.ph/CHto-takoe-Obnovit-tokeny-Obnovlenie-tokenov-vruchnuyu-i-Uvedomleniya-ob-ocenkah-11-13">Что такое «Обновить токены», «Обновление токенов вручную» и «Уведомления об оценках»?</a>',
                                            reply_markup=await diary_settings_kb(callback.from_user.id),
                                            parse_mode='html')
    except TelegramBadRequest as e:
        if 'message is not modified' in str(e):
            pass
        else:
            await logger.error("Error in settings_diary")

@callback_diary.callback_query(F.data == 'change_notify_diary')
async def change_notify_diary(callback: CallbackQuery):
    user = callback.from_user.id

    is_notify = await get_user_with_notify_mark(user)

    async with async_session() as session:
        if is_notify:
            stmt = update(User).where(User.tg_id == user).values(notify_diary = False)
            await session.execute(stmt)
        else:
            stmt = update(User).where(User.tg_id == user).values(notify_diary = True)
            await session.execute(stmt)
        
        await session.commit()
    
    await settings_diary(callback)


@callback_diary.callback_query(F.data == 'refreshing_tokens')
async def refreshing_tokens(callback: CallbackQuery):
    user = callback.from_user.id

    res = await refresh_token(user)
    
    if res == 'success':
        await callback.answer('✅ Токены успешно обновлены!', show_alert=True)
    else:
        await callback.answer('❎ Обновление провалилось... Обновите вручную', show_alert=True)

    await settings_diary(callback)