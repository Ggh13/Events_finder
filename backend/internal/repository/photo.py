from pkg.postgres.postgres import Database
from internal.models.models import Photo

from internal.entity.base import PhotoCreate

from typing import List

from sqlalchemy import insert
from sqlalchemy.dialects import postgresql


class PhotoRepository:
    def __init__(self, database: Database):
        self.database = database
    
    async def create_photo(self, photo_create: PhotoCreate) -> int | None:
        """Вставить ссылку на фото"""
        stmt = insert(Photo).values(
            url = photo_create.url
        ).returning(Photo.id)


        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect() 
        )

        sql = str(compiled)
        params = compiled.params

        row = await self.database.fetchrow(sql, *params.values())
        if row is None:
            return None
        
        print(row, flush=True)

        return dict(row)["id"]
    

    async def create_photos(self, photos_create: List[PhotoCreate]) -> List[int] | None:
        """Вставить несколько ссылок на фото и вернуть их ID"""
        if not photos_create:
            return []
        
        # Создаем список значений для вставки
        values_list = []
        for photo_create in photos_create:
            values_list.append({"url": photo_create.url})
        
        # Создаем запрос для вставки нескольких записей
        stmt = insert(Photo).values(values_list).returning(Photo.id)
        
        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect() 
        )
        
        sql = str(compiled)
        print(sql, flush=True)
        params = compiled.params
        print(params, flush=True)
        
        # Используем fetchall для получения всех строк
        rows = await self.database.fetch(sql, *params.values())
        if not rows:
            return None
        
        print(f"Создано {len(rows)} фото", flush=True)

        print(rows, flush=True)
        
        # Извлекаем ID из всех строк
        return [dict(row)["id"] for row in rows]
    
    
