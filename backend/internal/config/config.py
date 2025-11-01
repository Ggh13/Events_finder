from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from pkg.postgres.postgres import PostgresConfig
from pkg.redis.redis import RedisConfig

class Config(BaseSettings):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    #s3: S3Config = Field(default_factory=S3Config)
    
    rest_host: str = Field("0.0.0.1", alias="REST_HOST")
    rest_port: int = Field(8000, alias="REST_PORT")
    
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REST_"
        case_sensitive = False