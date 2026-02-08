from aiogram import Router

from .callback import router as callback_router
from .handler import router as handler_router

valentine_day_router = Router(name='valentine_day_router')

valentine_day_router.include_routers(callback_router,
                                     handler_router)

__all__ = ['valentine_day_router']