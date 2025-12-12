from fastapi import FastAPI
from typing import Optional, Tuple
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from typing import Optional, Tuple
import uvicorn
import asyncio
import sys
import os

from pkg.logger.logger import Logger

class RouterConfig(BaseSettings):
    host: str = Field(..., env="REST_HOST")
    port: int = Field(5432, env="REST_PORT")
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REST_"
        case_sensitive = False

    
class Router:
    def __init__(self, cfg: RouterConfig):
        self.serve = FastAPI()
        self.config = uvicorn.Config(
            self.serve,
            host=cfg.host,
            port=cfg.port,
            log_level="info"
        )
        self.server = uvicorn.Server(self.config)
        
        @self.serve.get("/")
        async def root():
            return {"message": "Hello World"}

        @self.serve.get("/health")
        async def health():
            return {"status": "healthy"}

        @self.serve.get("/api")
        async def root():
            return {"message": "Hello World"}

        @self.serve.get("/api/health")
        async def health():
            return {"status": "healthy"}
        
    async def run(self):
        await self.server.serve()