from aiogram import Bot, Dispatcher, types
from pydantic_settings import BaseSettings
from pydantic import Field

from internal.bot.routers import router as main_router

import logging


class BotConfig(BaseSettings):
    token: str = Field(..., alias="BOT_TOKEN")
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REST_"
        case_sensitive = False


class TelegramBot:
    def __init__(self, cfg: BotConfig):
        self.token = cfg.token
        print(self.token)
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        
        logging.basicConfig(level=logging.INFO)

        self.dp.include_router(main_router)
        
        

    async def run(self):
        await self.dp.start_polling(self.bot)
