import os
from dataclasses import dataclass
import torch 
from typing import List
from pathlib import Path
from dotenv import load_dotenv

env_path = "./../config/.env"
load_dotenv(env_path)

@dataclass
class Config:

    APP_NAME: str = os.getenv("APP_NAME", "posts_classifier")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    MODEL_PATH: str = os.getenv("MODEL_PATH", "model_weights/best_model.pth")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "google-bert/bert-base-uncased")
    IMAGE_SIZE: int = int(os.getenv("IMAGE_SIZE", "224"))
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "512"))
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

    CLASSES: tuple = (
        'acmmisis',
        'aiknowledgeclub',
        'art_klaster',
        'itatmisis',
        'nust_misis',
        'sportmisis',
        'youthmisis'
    )

    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")

config = Config()