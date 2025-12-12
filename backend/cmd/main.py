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

async def start():
    cfg = Config()
    print("Config loaded:", cfg, flush=True)
    
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
    
    router = Router(cfg.rest)
    
    await router.run()

    
if __name__ == "__main__":
    asyncio.run(start())
