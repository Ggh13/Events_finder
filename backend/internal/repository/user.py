import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List

from internal.models.models import TelegramInfo, User, UserCategory
from internal.entity.base import TelegramInfoCreate, UserCreate, TelegramInfoRead, UserRead, UserUpdate, CategoryBase, EventRead
from pkg.postgres.postgres import Database
from internal.models.models import Category, Event, EventCategory
from sqlalchemy import insert, select, update
from sqlalchemy.dialects import postgresql
from asyncpg import exceptions

from typing import Optional, Dict, Any

from asyncpg import exceptions
from fastapi import HTTPException

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.dialects import postgresql


class UserRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
    
    def _convert_role_to_db_format(self, role) -> str:
        """Преобразует роль из формата Pydantic в формат БД (enum использует полные названия)"""
        # В БД enum использует полные названия: 'PARTICIPANT', 'ADMIN', 'ORGANISER', 'DISTRIBUTOR'
        # Если это enum, берем его значение
        if hasattr(role, 'value'):
            return role.value
        else:
            return str(role)
    
    def _convert_role_from_db_format(self, role) -> str:
        """Преобразует роль из формата БД в формат Pydantic (enum использует полные названия)"""
        # В БД enum использует полные названия: 'PARTICIPANT', 'ADMIN', 'ORGANISER', 'DISTRIBUTOR'
        # Если это enum, берем его значение
        if hasattr(role, 'value'):
            return role.value
        else:
            return str(role)

    async def get_distributors(self, team_name: str) -> List[TelegramInfoRead] | None:
        """
        Получить дистрибьюторов с использованием сырого SQL
        """
        try:
            sql = """
                SELECT ti.*
                FROM events_finder.telegram_info ti
                JOIN events_finder.user u ON ti.id = u.telegram_id
                JOIN events_finder.user_team ut ON u.id = ut.user_id
                JOIN events_finder.team t ON ut.team_id = t.id
                WHERE u.role = 'DISTRIBUTOR'
                AND t.name = $1
            """
            
            rows = await self.database.fetch(sql, team_name)
            
            if not rows:
                return []
            
            distributors = []
            for row in rows:
                try:
                    telegram_read = TelegramInfoRead.model_validate(dict(row), from_attributes=True)
                    distributors.append(telegram_read)
                except Exception as e:
                    print(f"Ошибка при преобразовании TelegramInfo: {e}", flush=True)
                    continue
            
            return distributors
            
        except Exception as e:
            print(f"Ошибка при получении дистрибьюторов (SQL): {e}", flush=True)
            return None
    
    
    async def create_tg_info(self, tg_create: TelegramInfoCreate) -> int | None:
        """Вставить информацию из телеграмма """
        stmt = insert(TelegramInfo).values(
            telegram_id = tg_create.telegram_id,
            username = tg_create.username,
            chat_id =  tg_create.chat_id).returning(TelegramInfo.id)
        
        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect() 
        )

        sql = str(compiled)
        params = compiled.params

        try:
            row = await self.database.fetchrow(sql, *params.values())
            if row is None:
                return None
            print(row)
            return dict(row)["id"]
        except exceptions.UniqueViolationError:
            print("Already exists")
            return None
    
    async def get_telegram_info(self, telegram_id: int) -> TelegramInfoRead | None:
        """Получить инфу из телеграмма по telegram_id""" 
        stmt = select(TelegramInfo).filter(TelegramInfo.telegram_id == telegram_id)

        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect() 
        )
        sql = str(compiled)
        params = compiled.params

        row = await self.database.fetchrow(sql, *params.values())
        if row is None:
            return None

        res = TelegramInfoRead.model_validate(dict(row), from_attributes=True)
        return res

    async def get_or_create_telegram_info_id(self, tg_id: int, username: str, chat_id: int) -> int:
        stmt = (
            pg_insert(TelegramInfo)
            .values(telegram_id=tg_id, username=username, chat_id=chat_id)
            .on_conflict_do_update(
                index_elements=[TelegramInfo.telegram_id],
                set_={"username": username, "chat_id": chat_id},
            )
            .returning(TelegramInfo.id)
        )

        compiled = stmt.compile(dialect=postgresql.asyncpg.dialect(), compile_kwargs={"render_postcompile": True})
        row = await self.database.fetchrow(str(compiled), *compiled.params.values())
        return int(dict(row)["id"])

    async def create_user(self, user_create: UserCreate):
        # 1) достаём данные telegram_info из payload
        if not user_create.telegram_info:
            raise HTTPException(status_code=422, detail="telegram_info is required")

        tg_id = user_create.telegram_info.telegram_id
        username = user_create.telegram_info.username
        chat_id = user_create.telegram_info.chat_id

        # 2) пробуем найти telegram_info.id по telegram_id
        stmt_find = select(TelegramInfo.id).where(TelegramInfo.telegram_id == tg_id)
        compiled_find = stmt_find.compile(dialect=postgresql.asyncpg.dialect(), compile_kwargs={"render_postcompile": True})
        row = await self.database.fetchrow(str(compiled_find), *compiled_find.params.values())

        if row is None:
            # 3) если нет — создаём telegram_info и берём его id
            stmt_ti = (
                insert(TelegramInfo)
                .values(telegram_id=tg_id, username=username, chat_id=chat_id)
                .returning(TelegramInfo.id)
            )
            compiled_ti = stmt_ti.compile(dialect=postgresql.asyncpg.dialect(), compile_kwargs={"render_postcompile": True})
            row_ti = await self.database.fetchrow(str(compiled_ti), *compiled_ti.params.values())
            telegram_info_id = int(dict(row_ti)["id"])
        else:
            telegram_info_id = int(dict(row)["id"])

        # 4) создаём user с FK на telegram_info.id
        # Преобразуем роль из формата Pydantic ('ORGANISER') в формат БД ('O')
        db_role = self._convert_role_to_db_format(user_create.role)
        print(f"DEBUG: Creating user with role - Original: {user_create.role} (type: {type(user_create.role)}), Converted to DB: {db_role}", flush=True)
        
        stmt = (
            insert(User)
            .values(
                telegram_id=telegram_info_id,  # FK на telegram_info.id
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                photo_id=user_create.photo_id,
                balance=user_create.balance,
                role=db_role,
                longitude=float(user_create.longitude),
                latitude=float(user_create.latitude),
            )
            .returning(User.id)
        )

        compiled = stmt.compile(dialect=postgresql.asyncpg.dialect(), compile_kwargs={"render_postcompile": True})

        try:
            row = await self.database.fetchrow(str(compiled), *compiled.params.values())
            return int(dict(row)["id"])
        except exceptions.UniqueViolationError as e:
            return 2
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"DB error: {e}")



    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserRead]:
        """
        Получить пользователя по telegram_id из таблицы telegram_info
        с использованием JOIN
        """
        print(f"DEBUG: get_user_by_telegram_id called with telegram_id: {telegram_id}", flush=True)
        
        # Создаем JOIN между таблицами user и telegram_info
        stmt = (
            select(User).join(TelegramInfo, User.telegram_id == TelegramInfo.id)
            .where(TelegramInfo.telegram_id == telegram_id)
        )
        
        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect(),
            compile_kwargs={"render_postcompile": True}
        )
        
        sql = str(compiled)
        params = compiled.params
        
        print(f"DEBUG: SQL query: {sql}", flush=True)
        print(f"DEBUG: SQL params: {params.values()}", flush=True)
        
        row = await self.database.fetchrow(sql, *params.values())
        if row is None:
            print(f"DEBUG: No user found with telegram_id: {telegram_id}", flush=True)
            return None
        
        print(f"DEBUG: Found user row: {dict(row)}", flush=True)
        
        try:
            # Преобразуем строку в словарь и создаем объект UserRead
            user_dict = dict(row)
            
            # Роль в БД уже в формате полных названий ('ORGANISER', 'PARTICIPANT', etc.), 
            # но может быть enum объектом, поэтому преобразуем в строку
            if 'role' in user_dict:
                user_dict['role'] = self._convert_role_from_db_format(user_dict['role'])
            
            print(f"DEBUG: User dict before validation: {user_dict}", flush=True)
            return UserRead.model_validate(user_dict, from_attributes=True)
        except Exception as e:
            print(f"Ошибка при создании UserRead: {e}", flush=True)
            print(f"DEBUG: Row data: {dict(row) if row else None}", flush=True)
            return None

    async def add_category_to_user(
    self,
    user_id: int,
    category_in: CategoryBase,
) -> Optional[tuple[int, str]]:
        stmt = (
            insert(UserCategory)
            .values(user_id=int(user_id), category_id=int(category_in.id_cat))
            .returning(UserCategory.user_id, UserCategory.category_id)
        )

        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect(),
            compile_kwargs={"render_postcompile": True},
        )
        sql = str(compiled)
        params = compiled.params

        try:
            row = await self.database.fetchrow(sql, *params.values())
            if row is None:
                return None
            return ( row["category_id"])
        except exceptions.UniqueViolationError:
            return (UserCategory.category_id)


    async def get_recomend_post(self, user_id: int) -> Optional[EventRead]:
        """Вернуть 1 случайный event, у которого есть категория из user_category для user_id=user_id."""

        subq = (
            select(Event.id.label("event_id"))
            .join(EventCategory, EventCategory.event_id == Event.id)
            .join(UserCategory, UserCategory.category_id == EventCategory.category_id)
            .where(UserCategory.user_id == user_id)
            .distinct()
            .subquery()
        )

        # 2) по этим id выбираем полный Event и рандомим уже снаружи
        stmt = (
            select(Event)
            .join(subq, subq.c.event_id == Event.id)
            .order_by(func.random())
            .limit(1)
        )
        compiled = stmt.compile(dialect=postgresql.asyncpg.dialect())
        sql = str(compiled)
        params = compiled.params

        print(sql)
        print(*params.values())

        row = await self.database.fetchrow(sql, *params.values())
        if row is None:
            return None

        # fetchrow возвращает колонки event; приводим к dict и валидируем
        return EventRead.model_validate(dict(row), from_attributes=True)