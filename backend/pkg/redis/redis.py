from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

class RedisConfig(BaseSettings):
    host: str = Field("localhost", alias="REDIS_HOST")
    port: int = Field(6379, alias="REDIS_PORT")
    password: str = Field(1234, alias="REDIS_PASS")
    database: int = Field(0, alias="REDIS_DB")
    
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REDIS_"
        case_sensitive = False
        
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"