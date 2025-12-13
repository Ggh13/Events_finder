from fastapi import FastAPI
from typing import Optional, Tuple
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from typing import Optional, Tuple
import uvicorn
import asyncio
import sys
import os
from fastapi.middleware.cors import CORSMiddleware

from internal.entity.base import EventCreate

from pkg.logger.logger import Logger

class RouterConfig(BaseSettings):
    host: str = Field(..., alias="REST_HOST")
    port: int = Field(5432, alias="REST_PORT")
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REST_"
        case_sensitive = False

    
class Router:
    def __init__(self, cfg: RouterConfig):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.config = uvicorn.Config(
            self.app,
            host=cfg.host,
            port=cfg.port,
            log_level="info"
        )
        self.server = uvicorn.Server(self.config)
        
        @self.app.get("/")
        async def root():
            return {"message": "Hello World"}

        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}

        @self.app.get("/api")
        async def root():
            return {"message": "Hello World"}

        @self.app.get("/api/health")
        async def health():
            return {"status": "healthy"}
        
        @self.app.post("/api/create_event")
        async def create_event(event: EventCreate):
            print(event)
            return {"status": "ok"}
        
    async def run(self):
        await self.server.serve()