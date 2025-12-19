__all__ = ("router", )

from aiogram import Router
from .organiser import router as organiser_router
from .user import router as user_router

router = Router(name=__name__)

router.include_routers(
    organiser_router
    user_router
)