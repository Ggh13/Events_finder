from fastapi import FastAPI
from typing import Optional, Tuple

import uvicorn
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from internal.config.config import Config
from pkg.postgres.postgres import Database

from db.migrations.env import run_migrations

from internal.rest.rest import Router


async def start():
    cfg = Config()
    print("Config loaded:", cfg)

    run_migrations(cfg.postgres.async_url)
    
    # База данных постгрес - передавать только  слой репозитория
    psgDB = Database(cfg.postgres)
    
    success, err = await psgDB.Connect()
    if success == False:
        print(err)
        return
    
    success, err = await psgDB.PingDB()
    if success == False:
        print(err)
        return
    
    # Роутинг ручек передавать в слой хэндлеров
    router = Router(cfg.rest)
    
    await router.run()

    
if __name__ == "__main__":
    asyncio.run(start())
