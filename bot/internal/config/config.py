from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from internal.bot.bot import BotConfig

class Config(BaseSettings):
    bot: BotConfig = Field(default_factory=BotConfig)

    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

settings = Config()