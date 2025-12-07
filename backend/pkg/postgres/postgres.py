from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from typing import Optional, Tuple
import asyncpg

class PostgresConfig(BaseSettings):
    host: str = Field(..., alias="POSTGRES_HOST")
    port: int = Field(5432, alias="POSTGRES_PORT")
    user: str = Field(..., alias="POSTGRES_USER")
    password: str = Field(..., alias="POSTGRES_PASS")
    database: str = Field(..., alias="POSTGRES_DB")
    min_conn: int = Field(1, alias="POSTGRES_MIN_CONN")
    max_conn: int = Field(2, alias="POSTGRES_MAX_CONN")
    
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "POSTGRES_"
        case_sensitive = False
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
 
class Database:
    def __init__(self, cfg: PostgresConfig):
        self.cfg = cfg
        self.pool: Optional[asyncpg.Pool] = None
    async def Connect(self) -> Tuple[bool, str]:
        try:
            self.pool = await asyncpg.create_pool(
                user=self.cfg.user,
                password=self.cfg.password,
                database=self.cfg.database,
                host=self.cfg.host,
                port=self.cfg.port,
                min_size=self.cfg.min_conn,  # minimum conn count
                max_size=self.cfg.max_conn  # maximum conn count
            )
            return (True, "")
        except Exception as e:
            return (False, f"Connect error: { str(e) }")
        
    async def PingDB(self) -> Tuple[bool, str]:
        """
        Pings the PostgreSQL database using asyncpg by attempting a simple query.
        Returns True if the ping is successful, False otherwise.
        """
        try:
            await self.fetch('SELECT 1')
            await self.pool.close()
            return (True, "")
        except asyncpg.exceptions.PostgresError as e:
            return (False, f"Database connection error: {e}")
        except Exception as e:
            return (False, f"An unexpected error occurred: {e}")
    
    async def disconnect(self):
        """Закрытие пула подключений"""
        if self.pool:
            await self.pool.close()
    
    async def fetch(self, query: str, *args):
        """Выполнение SELECT запроса"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Выполнение SELECT запроса с возвратом одной строки"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute(self, query: str, *args):
        """Выполнение INSERT/UPDATE/DELETE запроса"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)