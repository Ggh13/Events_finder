import os
from dataclasses import dataclass
import torch 
from typing import List

@dataclass
class Config:

    APP_NAME: str = "posts_classifier"

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    MODEL_PATH: str = os.getenv("MODEL_PATH", "model_weights/best_model.pth")
    MODEL_NAME: str = "google-bert/bert-base-uncased"
    IMAGE_SIZE: int = 224
    MAX_TEXT_LENGTH: int = 512
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

    API_PREFIX: str = '/api/v1'

config = Config()