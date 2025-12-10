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

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

async def start():
    cfg = Config()
    print("Config loaded:", cfg)

    run_migrations(cfg.postgres.async_url)
    
    psgDB = Database(cfg.postgres)
    
    success, err = await psgDB.Connect()
    if success == False:
        print(err)
        return
    
    success, err = await psgDB.PingDB()
    if success == False:
        print(err)
        return
    
    config = uvicorn.Config(
        app,
        host=cfg.rest_host,
        port=cfg.rest_port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start())
