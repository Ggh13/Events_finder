import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from internal.models.models import TelegramInfo, User
from internal.entity.base import TelegramInfoCreate, UserCreate, TelegramInfoRead, UserRead
from pkg.postgres.postgres import Database

from sqlalchemy import insert, select, update
from sqlalchemy.dialects import postgresql
from asyncpg import exceptions

from typing import Optional, Dict, Any


class UserRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
    
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
    
    async def create_user(self, user_create: UserCreate) -> Optional[int]:
        """Создание пользователя в базе данныx"""

        stmt = insert(User).values(telegram_id = user_create.telegram_info.id,
            first_name = user_create.first_name,
            last_name = user_create.last_name,
            photo_id = user_create.photo_id,  
            balance = user_create.balance,
            role = str(user_create.role.value),
            longitude = float(user_create.longitude),
            latitude = float(user_create.latitude)
        ).returning(User.id)

        compiled = stmt.compile(dialect=postgresql.asyncpg.dialect(), compile_kwargs={"render_postcompile": True})
        sql = str(compiled)
        params = compiled.params

        print(sql)
        print(*params.values())

        try:
            row = await self.database.fetchrow(sql, *params.values())
            if row is None:
                return None
            print(row)
            return dict(row)["id"]
        except exceptions.UniqueViolationError as e:
            print(f"User creation failed - unique violation: {e}", flush=True)
            return None
        except Exception as e:
            print(f"User creation failed: {e}", flush=True)
            return None
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserRead]:
        """
        Получить пользователя по telegram_id из таблицы telegram_info
        с использованием JOIN
        """
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
        
        row = await self.database.fetchrow(sql, *params.values())
        if row is None:
            return None
        
        try:
            # Преобразуем строку в словарь и создаем объект UserRead
            user_dict = dict(row)
            return UserRead.model_validate(user_dict, from_attributes=True)
        except Exception as e:
            print(f"Ошибка при создании UserRead: {e}", flush=True)
            return None