import io
from typing import Tuple
import torch
from PIL import Image
from torchvision import transforms
from transformers import AutoTokenizer
from config import config

class DataProcessor:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        self.transform = self._get_image_transform()

    def _get_image_transform(self) -> transforms.Compose:
        return transforms.Compose([
            transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def process_text(self, text: str) -> tuple[torch.Tensor, torch.Tensor]:
        tokens = self.tokenizer(
            text,
            max_length=config.MAX_TEXT_LENGTH,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return tokens['input_ids'], tokens['attention_mask']
    
    def process_image(self, image: Image.Image) -> torch.Tensor:
        return self.transform(image).unsqueeze(0)
    
    def from_bytes_to_image(self, image_bytes: bytes) -> torch.Tensor:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self.process_image(image)