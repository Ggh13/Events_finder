from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from typing import Optional, Tuple
import asyncpg

class Logger(BaseSettings):
    def __init__(self):
        ...