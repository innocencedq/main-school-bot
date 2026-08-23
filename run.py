import asyncio
import logging
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.components.diary.vault import notify_last_marks
from config import tg_token
from app.components.routers.handlers import router
from app.database.data import async_main
from app.components.notifyprocesses.vk_notify import send_new_posts
from app.components.routers.callbacks import router_callback
from app.components.routers.admin import router_adm
from app.components.routers.inline_mode import router_inline_mode
from app.components.diary.callback_diary import callback_diary
from app.supportfunctions.check_users import remove_blocked_users
from app.supportfunctions.redis_misc import redis
from app.components.routers.tickets.topics import topic_router
from app.components.routers.func_admin.schedule_changer import router_adm as checker_router
from app.components.routers.valentine_day import valentine_day_router
from app.components.routers.func_admin.webadmin.web import app as web_admin
from app.supportfunctions.main_utils import get_server_ip

bot = Bot(token=tg_token)

#Функция инициализации
async def main():
    await async_main()
    
    ip = get_server_ip()
    config = uvicorn.Config(web_admin, host=ip, port=8000, log_level='info')
    webka = uvicorn.Server(config)
    
    asyncio.create_task(remove_blocked_users())
    asyncio.create_task(send_new_posts())
    asyncio.create_task(notify_last_marks())

    dp = Dispatcher(storage=RedisStorage(redis))
    dp.include_routers(router, 
                       router_callback, 
                       router_adm, 
                       router_inline_mode, 
                       callback_diary, 
                       topic_router,
                       checker_router,
                       valentine_day_router)

    await asyncio.gather(
        webka.serve(),
        dp.start_polling(bot)
        )


#Точка входа
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        logging.error(e)