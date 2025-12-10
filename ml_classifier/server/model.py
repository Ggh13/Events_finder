import torch
import torch.nn as nn
from torchvision import models
from transformers import AutoModel
from config import config

model_name = config.MODEL_NAME
class MultiModel(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.text_model = AutoModel.from_pretrained(model_name) #trust_remote_code=True
        self.image_model = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)#, pretrained=True
        self.image_model.fc = nn.Identity()

        total_bert_layers = len(self.text_model.encoder.layer)
        for param in self.text_model.parameters():
            param.requires_grad = False
        bert_unfreez = 1
        for i in range(total_bert_layers - bert_unfreez, total_bert_layers):
            for param in self.text_model.encoder.layer[i].parameters():
                param.requires_grad = True
        for param in self.text_model.pooler.parameters():
            param.requires_grad = True

        for param in self.image_model.parameters():
            param.requires_grad = False
        # for param in self.image_model.layer3.parameters():
        #     param.requires_grad = True
        for param in self.image_model.layer4.parameters():
            param.requires_grad = True

        self.num_classes = num_classes
        text_output = self.text_model.config.hidden_size
        image_output = 512
        comb_out = text_output + image_output
        self.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(comb_out, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, self.num_classes)
        )
    
    def forward(self, input_ids, attention_mask, image):
        text_features = self.text_model(
            input_ids = input_ids, 
            attention_mask = attention_mask
        ).pooler_output

        image_features = self.image_model(image)

        comb = torch.cat([text_features, image_features], dim=1)

        return self.classifier(comb)