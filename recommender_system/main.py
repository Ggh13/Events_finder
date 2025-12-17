from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from recsys_handler import recommend
from config.settings import settings

app = FastAPI(
    title="Recommendation System API",
    description="API для рекомендации категорий",
    version="1.0.0",
    debug=settings.DEBUG
)


class ItemsRequest(BaseModel):
    categories: List[str]
    top_k: Optional[int] = None

@app.post("/api/add_category/",
          tags=['Рекомендательная система'],
          summary='Рекомендовать подходящие категории',
          response_description="Список рекомендованных категорий")
async def recommend_categories(items: ItemsRequest):
    response = recommend(items.categories, items.top_k)
    return response

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
