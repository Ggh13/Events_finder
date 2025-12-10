import torch
import io
from typing import Dict
from PIL import Image
from dataclasses import dataclass

from model import MultiModel
from processor import DataProcessor
from config import config

@dataclass
class Predict:
    class_name: str
    conf: float


class ClassifierServ:
    def __init__(self):
        self.model = None
        self.processor = DataProcessor()
        self.device = torch.device(config.DEVICE)
        self._load_model()
    
    def _load_model(self):
        self.model = MultiModel(len(config.CLASSES))
        checkpoint = torch.load(config.MODEL_PATH, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        self.model.to(self.device)

    def predict(self, text: str, image: Image.Image = None) -> Predict:
        input_ids, attention_mask = self.processor.process_text(text)
        input_ids = input_ids.to(self.device)
        attention_mask = attention_mask.to(self.device)

        if image is not None:
            image = self.processor.process_image(image).to(self.device)
        else:
            image = torch.ones(1, 3, config.IMAGE_SIZE, config.IMAGE_SIZE).to(self.device)

        
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask, image)
            probs = torch.softmax(outputs, dim=1)
            pred_idx = probs.argmax(dim=1).item()

        predict = Predict(
            config.CLASSES[pred_idx],
            float(probs.squeeze()[pred_idx])
            )
        
        return predict
    
    def bytes_predict(self, text: str, image_bytes: bytes = None) -> Predict:
        image = None
        if image_bytes is not None:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        return self.predict(text, image)
