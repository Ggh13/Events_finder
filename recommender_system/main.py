from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from recsys_handler import recommend

app = FastAPI()

class ItemsRequest(BaseModel):
    categories: List[str]

@app.post("/add_category/",
          tags=['Рекомендательная система'],
          summary='Рекомендовать 5 подходящих категорий')
async def recommend_categories(items: ItemsRequest):
    response = recommend(items.categories, 5)
    return response
