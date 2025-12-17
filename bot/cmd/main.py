from typing import Optional, Tuple

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from internal.config.config import Config

from internal.bot.bot import TelegramBot


async def start():
    cfg = Config()
    print("Config loaded:", cfg, flush=True)

    bot = TelegramBot(cfg.bot)

    await bot.run()

    
if __name__ == "__main__":
    asyncio.run(start())
