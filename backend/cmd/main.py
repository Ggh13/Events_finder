from fastapi import FastAPI
from typing import Optional, Tuple

import uvicorn
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from internal.config.config import Config
from pkg.postgres.postgres import Database

from internal.rest.rest import Router

from pkg.postgres.postgres import Database

from internal.repository.user import UserRepository
from internal.repository.photo import PhotoRepository
from internal.repository.event import EventRepository

from internal.service.organiser import OrganiserService

async def start():
    cfg = Config()
    print("Config loaded:", cfg, flush=True)
    
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

    success, err = await psgDB.Connect()
    if success == False:
        print(err)
        return
    
    user_repo = UserRepository(psgDB)
    photo_repo = PhotoRepository(psgDB)
    event_repo = EventRepository(psgDB)

    event_service = OrganiserService(user_repo=user_repo, photo_repo=photo_repo, event_repo=event_repo)
    
    # Роутинг ручек передавать в слой хэндлеров
    router = Router(cfg.rest, event_service)

    
    await router.run()

    
if __name__ == "__main__":
    asyncio.run(start())
