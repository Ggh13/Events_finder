from fastapi import FastAPI
from typing import Optional, Tuple
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from typing import Optional, Tuple
import uvicorn
import asyncio
import sys
import os

from internal.config.config import Config
from pkg.logger.logger import Logger

class TestEndpoints(BaseSettings):
    def __init__(self):
        