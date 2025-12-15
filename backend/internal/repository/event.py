from pkg.postgres.postgres import Database
from internal.models.models import EventPhoto, Event, EventCategory, Photo, Category, EventCategory

from internal.entity.base import EventCreate, EventRead, PhotoCreate, EventUpdate

from typing import List

from sqlalchemy import insert, select, update, func
from sqlalchemy.dialects import postgresql


class EventRepository:
    def __init__(self, database: Database):
        self.database = database
    
    async def create_event(self, new_event: EventCreate, photo_ids: List[int]) -> int | None:
        """Простая версия создания мероприятия"""
        # 1. Создаем мероприятие
        stmt = insert(Event).values(
            name=new_event.name,
            description=new_event.description,
            date=new_event.date,
            address=new_event.address,
            longitude=float(new_event.longitude),
            latitude=float(new_event.latitude),
            age_restriction=new_event.age_restriction,
            chat_link=new_event.chat_link,
            organiser_id=new_event.organiser_id,
            max_participants=new_event.max_participants,
            cost=new_event.cost,
            balance=new_event.balance,
            is_freezed=new_event.is_freezed
        ).returning(Event.id)
        
        compiled = stmt.compile(dialect=postgresql.asyncpg.dialect())
        sql = str(compiled)
        params = compiled.params
        
        row = await self.database.fetchrow(sql, *params.values())
        if not row:
            return None
        
        event_id = dict(row)["id"]
        
        # 2. Привязываем фото
        if photo_ids:
            photos_data = [{"event_id": event_id, "photo_id": pid} for pid in photo_ids]
            stmt_photos = insert(EventPhoto).values(photos_data)
            compiled_photos = stmt_photos.compile(dialect=postgresql.asyncpg.dialect())
            await self.database.execute(str(compiled_photos), *compiled_photos.params.values())
        
        # 3. Привязываем категории
        if new_event.category_ids:
            categories_data = [{"event_id": event_id, "category_id": cid} for cid in new_event.category_ids]
            stmt_cats = insert(EventCategory).values(categories_data)
            compiled_cats = stmt_cats.compile(dialect=postgresql.asyncpg.dialect())
            await self.database.execute(str(compiled_cats), *compiled_cats.params.values())
        
        return event_id

    async def get_event_by_id(self, event_id: int) -> EventRead | None:
        try:
            stmt = (
                select(Event)
                .where(Event.id == event_id)
            )
            
            compiled = stmt.compile(
                dialect=postgresql.asyncpg.dialect(),
                compile_kwargs={"render_postcompile": True}
            )
            
            sql = str(compiled)
            params = compiled.params
            
            row = await self.database.fetchrow(sql, *params.values())

            try:
                event_dict = dict(row)
                
                event = EventRead.model_validate(event_dict, from_attributes=True)

                stmt = select(Photo).join(EventPhoto, EventPhoto.photo_id == Photo.id).where(EventPhoto.event_id == event.id)
                compiled = stmt.compile(
                    dialect=postgresql.asyncpg.dialect(),
                    compile_kwargs={"render_postcompile": True}
                )
                sql = str(compiled)
                params = compiled.params
                
                photos = await self.database.fetch(sql, *params.values())
                # print("*****************************", flush=True)
                # print(photos, flush=True)
                i = 0
                for photo in photos:
                    print(i, dict(photo), flush=True)
                    event.photo_ids.append(PhotoCreate.model_validate(dict(photo), from_attributes=True))
                    i += 1
                print("*****************************", flush=True)
                print(event.photo_ids, flush=True)

                stmt = select(Category).join(EventCategory, EventCategory.category_id == Category.id).where(EventCategory.event_id == event.id)
                compiled = stmt.compile(
                    dialect=postgresql.asyncpg.dialect(),
                    compile_kwargs={"render_postcompile": True}
                )
                sql = str(compiled)
                params = compiled.params
                
                cats = await self.database.fetch(sql, *params.values())
                print("*****************************", flush=True)
                print(cats, flush=True)
                for cat in cats:
                    event.category_ids.append(dict(cat)["id"])

            except Exception as e:
                print(f"Ошибка при преобразовании мероприятия: {e}", flush=True)
                return None
            
            return event
            
        except Exception as e:
            print(f"Ошибка при получении мероприятий с пагинацией: {e}", flush=True)
            return None

    async def delete_event_by_id_compact(self, event_id: int) -> int | None:
        """Компактная версия удаления мероприятия"""
        try:
            # Удаляем связи с фото
            await self.database.execute(
                "DELETE FROM events_finder.event_photo WHERE event_id = $1",
                event_id
            )
            
            # Удаляем связи с категориями
            await self.database.execute(
                "DELETE FROM events_finder.event_category WHERE event_id = $1", 
                event_id
            )
            
            # Удаляем мероприятие и возвращаем ID
            row = await self.database.fetchrow(
                "DELETE FROM events_finder.event WHERE id = $1 RETURNING id",
                event_id
            )
            
            return row["id"] if row else None
        
        except Exception as e:
            print(f"Ошибка при удалении мероприятия {event_id}: {e}", flush=True)
            return None
    
    async def update_event_compact(self, event_update: EventUpdate) -> int | None:
        """Компактная версия обновления мероприятия"""
        try:
            # Извлекаем event_id
            event_id = event_update.event_id
            
            # Преобразуем в словарь, исключая None значения
            update_dict = event_update.dict(exclude_none=True)
            
            # Удаляем event_id из словаря обновления (это не поле для обновления)
            update_dict.pop('event_id', None)
            
            if not update_dict:
                print("Нет полей для обновления", flush=True)
                return event_id
            
            # Преобразуем float для decimal полей
            if 'longitude' in update_dict:
                update_dict['longitude'] = float(update_dict['longitude'])
            if 'latitude' in update_dict:
                update_dict['latitude'] = float(update_dict['latitude'])
            
            stmt = update(Event).where(Event.id == event_id).values(**update_dict).returning(Event.id)
            compiled = stmt.compile(dialect=postgresql.asyncpg.dialect())
            
            row = await self.database.fetchrow(str(compiled), *compiled.params.values())
            
            if row is None:
                print(f"Мероприятие с ID {event_id} не найдено", flush=True)
                return None
            
            return dict(row)["id"]
            
        except Exception as e:
            print(f"Ошибка обновления мероприятия: {e}", flush=True)
            return None

    async def get_events_by_user_paginated(
        self, 
        user_id: int, 
        limit: int = 3, 
        offset: int = 0
    ) -> List[EventRead] | None:
        """
        Получить мероприятия пользователя с пагинацией
        
        Args:
            user_id: ID пользователя (организатора)
            limit: количество мероприятий на странице
            offset: смещение
            
        Returns:
            Список мероприятий или None в случае ошибки
        """
        try:
            stmt = select(func.count()).select_from(Event).where(Event.organiser_id == user_id)

            compiled = stmt.compile(
                dialect=postgresql.asyncpg.dialect(),
                compile_kwargs={"render_postcompile": True}
            )
            
            sql = str(compiled)
            params = compiled.params

            row = await self.database.fetchrow(sql, *params.values())
            print("ROW: ", row, flush=True)

            total_cnt = dict(row)["count_1"]
            print("total", total_cnt, flush=True)
            stmt = (
                select(Event)
                .where(Event.organiser_id == user_id)
                .order_by(Event.date.desc())
                .limit(limit)
                .offset(offset)
            )
            
            compiled = stmt.compile(
                dialect=postgresql.asyncpg.dialect(),
                compile_kwargs={"render_postcompile": True}
            )
            
            sql = str(compiled)
            params = compiled.params
            
            rows = await self.database.fetch(sql, *params.values())
            
            if not rows:
                return []
            
            events = []
            for row in rows:
                try:
                    event_dict = dict(row)
                    
                    event_read = EventRead.model_validate(event_dict, from_attributes=True)

                    stmt = select(Photo).join(EventPhoto, EventPhoto.photo_id == Photo.id).where(EventPhoto.event_id == event_read.id)
                    compiled = stmt.compile(
                        dialect=postgresql.asyncpg.dialect(),
                        compile_kwargs={"render_postcompile": True}
                    )
                    sql = str(compiled)
                    params = compiled.params
                    
                    photos = await self.database.fetch(sql, *params.values())
                    # print("*****************************", flush=True)
                    # print(photos, flush=True)
                    i = 0
                    for photo in photos:
                        print(i, dict(photo), flush=True)
                        event_read.photo_ids.append(PhotoCreate.model_validate(dict(photo), from_attributes=True))
                        i += 1
                    print("*****************************", flush=True)
                    print(event_read.photo_ids, flush=True)

                    stmt = select(Category).join(EventCategory, EventCategory.category_id == Category.id).where(EventCategory.event_id == event_read.id)
                    compiled = stmt.compile(
                        dialect=postgresql.asyncpg.dialect(),
                        compile_kwargs={"render_postcompile": True}
                    )
                    sql = str(compiled)
                    params = compiled.params
                    
                    cats = await self.database.fetch(sql, *params.values())
                    print("*****************************", flush=True)
                    print(cats, flush=True)
                    for cat in cats:
                        event_read.category_ids.append(dict(cat)["id"])


                    events.append(event_read)
                except Exception as e:
                    print(f"Ошибка при преобразовании мероприятия: {e}", flush=True)
                    continue
            
            return (total_cnt, events)
            
        except Exception as e:
            print(f"Ошибка при получении мероприятий с пагинацией: {e}", flush=True)
            return (None, None)