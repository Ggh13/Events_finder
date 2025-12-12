from pkg.postgres.postgres import Database
from internal.models.models import Photo

from internal.entity.base import PhotoCreate

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
    
    
