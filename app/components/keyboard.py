from functools import lru_cache
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.database.requests import get_user_with_notify, get_list_admin, get_quick_menu, get_user_with_extended_diary, check_admin, get_refresh_token, get_last_advert_id, get_list_open_tickets, get_shift, get_user_with_notify_mark


#Клавиатура быстрой настройки
ask_notify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes_notify')],
    [InlineKeyboardButton(text='Нет', callback_data='no_notify')],
])

ask_quick_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes_quick_menu')],
    [InlineKeyboardButton(text='Нет', callback_data='no_quick_menu')],
])


#Быстрое меню
quick_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🗓 Расписание на сегодня')],
    [KeyboardButton(text='🏠 Главное меню')]
], resize_keyboard=True)


#Клавиатура главного меню
async def main_menu(user):
    builder = InlineKeyboardBuilder()
    
    advert_last_id = await get_last_advert_id()
    usage = await get_user_with_extended_diary(user)
    admin = await check_admin(user)

    builder.row(InlineKeyboardButton(text='🗓 Расписание', callback_data='rasp'), (InlineKeyboardButton(text='📒 Дневник', callback_data='main_diary')) if usage else InlineKeyboardButton(text='📒 Дневник', url='https://pwa.kiasuo.ru/'))
    # builder.add(InlineKeyboardButton(text='🎈 События', callback_data='events'))
    # builder.add(InlineKeyboardButton(text='📖 Исторические факты Великой Победы', callback_data='history'))
    builder.add(InlineKeyboardButton(text='📋 Объявления', callback_data=f'advert-{advert_last_id if advert_last_id else 0}'))
    builder.add(InlineKeyboardButton(text='⚪️ Официальная группа ВКонтакте', url='https://vk.com/public217585014'))
    builder.add(InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings'))
    # builder.add(InlineKeyboardButton(text='📮 День святого Валентина',callback_data='valentine_day'))
    builder.add(InlineKeyboardButton(text='Админ панель', callback_data='adminpanel')) if admin else None

    return builder.adjust(2, 1).as_markup()


#Одноразовая кнопка Главного меню для постов с ВК
async def for_vk_notify(user):
    quick_menu = await get_quick_menu(user)

    builder = ReplyKeyboardBuilder()

    if quick_menu is True:
        builder.add(KeyboardButton(text='🗓 Расписание на сегодня'))
        builder.add(KeyboardButton(text='🏠 Главное меню'))
        return builder.adjust(1).as_markup(resize_keyboard=True)

    elif quick_menu is False:
        builder.add(KeyboardButton(text='🏠 Главное меню'))
        return builder.adjust(1).as_markup(resize_keyboard=True, one_time_keyboard=True)

#Клавиатура настроек
async def settings_keyboard(user):
    notify = await get_user_with_notify(user)
    quick_menu = await get_quick_menu(user)
    diary = await get_user_with_extended_diary(user)

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🔔 Выключить уведомления о постах", callback_data='edit_settings') if notify else InlineKeyboardButton(text="🔕 Включить уведомления о постах", callback_data='edit_settings'))
    builder.add(InlineKeyboardButton(text="⌨️ Выключить быстрое меню", callback_data='quick_menu') if quick_menu else InlineKeyboardButton(text="⌨️ Включить быстрое меню", callback_data='quick_menu'))
    builder.add(InlineKeyboardButton(text="📒 Выключить расширенную кнопку дневника", callback_data='edit_diary') if diary else InlineKeyboardButton(text="📒 Включить расширенную кнопку дневника", callback_data='edit_diary'))
    builder.add(InlineKeyboardButton(text='🛠 Технический раздел', callback_data='bug_report'))
    builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))

    return builder.adjust(1).as_markup()

#Назад (настройки)
back_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='settings')],
])

#Назад (главное меню)
back_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')],
])

#Назад (главное меню) (малоиспользуемое!)
back_main_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ В главное меню', callback_data='back')],
    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
])


#Клавиатура расписаний
def get_rasp_keyboard(shift: str = "1") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📅 Понедельник', callback_data=f'schedule:{shift}:monday'), 
         InlineKeyboardButton(text='📅 Вторник', callback_data=f'schedule:{shift}:tuesday'), 
         InlineKeyboardButton(text='📅 Среда', callback_data=f'schedule:{shift}:wednesday')],
        [InlineKeyboardButton(text='📅 Четверг', callback_data=f'schedule:{shift}:thursday'), 
         InlineKeyboardButton(text='📅 Пятница', callback_data=f'schedule:{shift}:friday')],
        [InlineKeyboardButton(text='🔔 Звонки', callback_data='schedule:calls')],
        [InlineKeyboardButton(text=f'🔄 Сменить смену', callback_data=f'schedule_change_shift'), 
         InlineKeyboardButton(text='⚠️ Неточности в расписании?', callback_data='help_with_schedule')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')],
    ])

def get_day_keyboard(day: str, shift: str = "1") -> InlineKeyboardMarkup:
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    day_index = days_order.index(day)
    
    prev_day = days_order[(day_index - 1) % 5]
    next_day = days_order[(day_index + 1) % 5]
    
    page_number = day_index + 1

    from app.supportfunctions.main_utils import get_day_name
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'📆 {get_day_name(prev_day)}', callback_data=f'schedule:{shift}:{prev_day}'), 
         InlineKeyboardButton(text=f'{page_number}/5', callback_data='page'), 
         InlineKeyboardButton(text=f'📆 {get_day_name(next_day)}', callback_data=f'schedule:{shift}:{next_day}')],
        [InlineKeyboardButton(text=f'🔄 Сменить смену', callback_data=f'schedule_change_shift')],
        [InlineKeyboardButton(text='🔔 Звонки', callback_data='schedule:calls')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='rasp')]
    ])


def get_calls_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='rasp')]
    ])


def get_shift_selection_keyboard(current_shift: str = "1") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=('1 смена ✅' if current_shift == "1" else '1 смена'), callback_data='schedule_set_shift:1'),
         InlineKeyboardButton(text=('2 смена ✅' if current_shift == "2" else '2 смена'), callback_data='schedule_set_shift:2')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'rasp')]
    ])


class ScheduleKeyboards:
    @staticmethod
    def rasp(shift: str = "1") -> InlineKeyboardMarkup:
        return get_rasp_keyboard(shift)
    
    @staticmethod
    def monday(shift: str = "1") -> InlineKeyboardMarkup:
        return get_day_keyboard("monday", shift)
    
    @staticmethod
    def tuesday(shift: str = "1") -> InlineKeyboardMarkup:
        return get_day_keyboard("tuesday", shift)
    
    @staticmethod
    def wednesday(shift: str = "1") -> InlineKeyboardMarkup:
        return get_day_keyboard("wednesday", shift)
    
    @staticmethod
    def thursday(shift: str = "1") -> InlineKeyboardMarkup:
        return get_day_keyboard("thursday", shift)
    
    @staticmethod
    def friday(shift: str = "1") -> InlineKeyboardMarkup:
        return get_day_keyboard("friday", shift)
    
    @staticmethod
    def calls() -> InlineKeyboardMarkup:
        return get_calls_keyboard()
    
    @staticmethod
    def shift_selection(current_shift: str = "1") -> InlineKeyboardMarkup:
        return get_shift_selection_keyboard(current_shift)


#Уведомления
async def notify_all_schedule():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='🗓 Расписание', callback_data='rasp'))
    builder.add(InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide'))
    return builder.adjust(1).as_markup()


async def notify_schedule(day):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='🗓 Перейти', callback_data=day))
    builder.add(InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide'))
    return builder.adjust(1).as_markup()


notify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')],
])


async def advert_notify_new():
    last_advert_id = await get_last_advert_id()
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Объявления', callback_data=f'advert-{last_advert_id}'))
    builder.add(InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide'))

    return builder.adjust(1, 1).as_markup()


#Админ панель
admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❗️ Обновление расписания', callback_data='notify_schedule')],
    [InlineKeyboardButton(text='📋 Управление объявлениями', callback_data='advert_manage')],
    [InlineKeyboardButton(text='📝 Рассылка своего уведомления', callback_data='adm_message')],
    [InlineKeyboardButton(text='➕ Добавление администратора', callback_data='add_admin')],
    [InlineKeyboardButton(text='📄 Тикеты', callback_data='main_tickets')],
    [InlineKeyboardButton(text='⬅️ Назад в главное меню', callback_data='back')],
    [InlineKeyboardButton(text='♻️ Скрыть', callback_data='hide')]
])


async def manage_tickets():
    builder = InlineKeyboardBuilder()
    tickets = await get_list_open_tickets()

    for id in tickets:
        builder.add(InlineKeyboardButton(text=f'Тикет #{id}', callback_data=f'ticket-{id}'))
        
    return builder.adjust(1, 2).as_markup()
    


advert_manage_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать объявление', callback_data='advert_create')],
    [InlineKeyboardButton(text='Редактировать объявления', callback_data='advert_edit')],
    [InlineKeyboardButton(text='Назад', callback_data='adminpanel')]   
])


advert_skip_picture = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='advert_skip')]
])


advert_continue_picture = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='advert_next')]
])


advert_confirmed = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='advert_confirm')],
    [InlineKeyboardButton(text='Отменить', callback_data='advert_cancel')],
    [InlineKeyboardButton(text='Изменить заголовок', callback_data='advert_edit_title')],
    [InlineKeyboardButton(text='Изменить описание', callback_data='advert_edit_description')],
    [InlineKeyboardButton(text='Изменить/добавить изображение', callback_data='advert_edit_image')]
])


advert_edit_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отменить', callback_data='advert_edit_cancel')]
])

adm_update_schedule = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='schedule_update_confirm')],
    [InlineKeyboardButton(text='Отмена', callback_data='adminpanel')]
])


adm_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='adminpanel')]
])


send_own_message = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='adminpanel')]
])


manual_formatting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='adm_message')]
])


adm_rasp = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1. Обновить расписание на следующую неделю', callback_data='next_week_notify')],
    [InlineKeyboardButton(text='2. Внести изменение в текущее расписание', callback_data='day_change')],
    [InlineKeyboardButton(text='3. Обновить расписание звонков', callback_data='notify_calls')],
    [InlineKeyboardButton(text='4. Заполнить расписание заглушками', callback_data='zaglushka_schedule')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='adminpanel')],
])



confirm_adm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='adm_confirm')],
    [InlineKeyboardButton(text='Изменить текст', callback_data='adm_message')]
])


tech_works = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начало тех. работ', callback_data='tech_works_start')],
    [InlineKeyboardButton(text='Конец тех. работ', callback_data='tech_works_finish')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='adminpanel')]
])


repeat_adm = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Повторить', callback_data='adm_message')]])


confirm_schedule = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes_schedule')],
    [InlineKeyboardButton(text='Нет', callback_data='adminpanel')]
])


confirm_day = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes_day_change')],
    [InlineKeyboardButton(text='Нет', callback_data='adminpanel')]
])


confirm_calls = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes_calls_change')],
    [InlineKeyboardButton(text='Нет', callback_data='adminpanel')]
])


ann_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить объявление', callback_data='add_ann')],
    [InlineKeyboardButton(text='Редактировать объявление', callback_data='edit_ann')],
    [InlineKeyboardButton(text='Удалить объявление', callback_data='delete_ann')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='adminpanel')]
])


bug_report = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text='📄 Тикет', callback_data='bug')], # InlineKeyboardButton(text='💡 Идея', callback_data='idea')],
    # [InlineKeyboardButton(text='👷 Стать тестером', callback_data='add_test')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='settings')]
])


#Дневник
async def main_diary_kb(user):
    builder = InlineKeyboardBuilder()
    check_user = await get_refresh_token(user)
    if check_user != 'None':
        builder.add(InlineKeyboardButton(text='📑 Оценки', callback_data='marks'))
        builder.add(InlineKeyboardButton(text='📝 Домашняя работа', callback_data='get_homework'))
        builder.add(InlineKeyboardButton(text='📙 Дневник КИАСУО', url='https://pwa.kiasuo.ru/'))
        builder.add(InlineKeyboardButton(text='⚙️ Настройки дневника', callback_data='settings_diary'))
        builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))
    else:
        builder.add(InlineKeyboardButton(text='📱 Вход Android (Chrome)', callback_data='auth_android_chrome'))
        builder.add(InlineKeyboardButton(text='📱 Вход iOS (Safari)', callback_data='auth_ios_safari'))
        builder.add(InlineKeyboardButton(text='💻 Вход через ПК', callback_data='auth_pc'))
        builder.add(InlineKeyboardButton(text='📙 Дневник КИАСУО', url='https://pwa.kiasuo.ru/'))
        builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))
    return builder.adjust(2, 1).as_markup()


choose_marks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Четверть/полугодие', callback_data='get_all_marks'), InlineKeyboardButton(text='Последние 5 дней', callback_data='check_marks')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='main_diary')]
])


escape_from_marks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='marks')]
])


back_to_diary = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='main_diary')]
])


methods_auth = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📱 Вход Android (Chrome)', callback_data='auth_android_chrome'), InlineKeyboardButton(text='📱 Вход iOS (Safari)', callback_data='auth_ios_safari')],
    [InlineKeyboardButton(text='💻 Вход через ПК', callback_data='auth_pc')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='main_diary')]
])


async def diary_settings_kb(user):
    builder = InlineKeyboardBuilder()

    is_notify = await get_user_with_notify_mark(user)

    builder.add(InlineKeyboardButton(text='🔔 Выключить уведомеления об оценках', callback_data='change_notify_diary') if is_notify else InlineKeyboardButton(text='🔕 Включить уведомления об оценках', callback_data='change_notify_diary'))
    builder.add(InlineKeyboardButton(text='🔄️ Обновить токены', callback_data='refreshing_tokens'))
    builder.add(InlineKeyboardButton(text='✍️ Обновление токенов вручную', callback_data='methods_auth'))
    builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='main_diary'))

    return builder.adjust(1).as_markup()


async def advert_kb(curr_id: int, user):
    builder = InlineKeyboardBuilder()
    advert_last_id = int(await get_last_advert_id())
    is_admin = await check_admin(user)
    format_pages = advert_last_id - curr_id + 1


    builder.row(InlineKeyboardButton(text='<<', callback_data=f'advert-{(curr_id + 1) if curr_id != advert_last_id else 1}'),
                InlineKeyboardButton(text=f'{format_pages}/{advert_last_id}', callback_data='page'),
                InlineKeyboardButton(text='>>',  callback_data=f'advert-{(curr_id - 1) if curr_id != 1 else advert_last_id}')) # страницы
    builder.add(InlineKeyboardButton(text='➡️ В конец', callback_data=f'advert-{1}')) # к концу
    builder.add(InlineKeyboardButton(text='📝 Редактировать (admin)', callback_data=f'edit_advert-{curr_id}')) if is_admin else None
    builder.add(InlineKeyboardButton(text='⬅️ Назад', callback_data='back'))

    return builder.adjust(3, 1).as_markup()


async def advert_editing(curr_id):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Применить', callback_data=f'advert_editing_confirm-{curr_id}'),
                InlineKeyboardButton(text='Отменить', callback_data=f'advert-{curr_id}'))
    builder.add(InlineKeyboardButton(text='Изменить заголовок', callback_data='advert_edit_title'))
    builder.add(InlineKeyboardButton(text='Изменить описание', callback_data='advert_edit_description'))
    builder.add(InlineKeyboardButton(text='Изменить/добавить изображение', callback_data='advert_edit_image'))
    builder.add(InlineKeyboardButton(text='Удалить объявление', callback_data=f'delete_advert-{curr_id}'))

    return builder.adjust(2, 1).as_markup()


async def advert_continue_edit(advert_id):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Продолжить', callback_data=f'edit_advert-{advert_id}'))
    builder.add(InlineKeyboardButton(text='Отменить', callback_data=f'edit_advert-{advert_id}-cancel'))

    return builder.adjust(1).as_markup()
    