from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from pkg.postgres.postgres import PostgresConfig
from pkg.redis.redis import RedisConfig
from internal.rest.rest import RouterConfig

class Config(BaseSettings):
    rest: RouterConfig = Field(default_factory=RouterConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    #s3: S3Config = Field(default_factory=S3Config)
    
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False