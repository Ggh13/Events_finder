from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

class PostgresConfig(BaseSettings):
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(5432, env="POSTGRES_PORT")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., alias="POSTGRES_PASS")
    database: str = Field(..., alias="POSTGRES_DB")
    
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "POSTGRES_"
        case_sensitive = False
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"