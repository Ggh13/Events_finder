from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Paths (ВЫНОСИМ В КОНФИГ!)
    WEIGHT_MATRIX_PATH: str = os.getenv("WEIGHT_MATRIX_PATH", "weight_matrix.npy")

    # Recommendations
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", 5))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"


settings = Settings()