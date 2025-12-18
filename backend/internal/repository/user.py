import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from internal.models.models import TelegramInfo, User
from internal.entity.base import TelegramInfoCreate, UserCreate, TelegramInfoRead, UserRead, UserUpdate
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



    async def register_user(self, telegram_id: int, user: UserUpdate) -> Optional[UserRead]:
        # 1) Найти TelegramInfo.id по TelegramInfo.telegram_id
        tg_stmt = select(TelegramInfo.id).where(TelegramInfo.telegram_id == telegram_id)
        tg_compiled = tg_stmt.compile(
            dialect=postgresql.asyncpg.dialect(),
            compile_kwargs={"render_postcompile": True},
        )
        tg_row = await self.database.fetchrow(str(tg_compiled), *tg_compiled.params.values())
        if tg_row is None:
            return None
        telegram_info_id = tg_row["id"]

        # 2) Данные пользователя + проверки NOT NULL
        data = user.model_dump(exclude_unset=True)

        if data.get("first_name") is None or data.get("last_name") is None:
            return None
        if data.get("longitude") is None or data.get("latitude") is None:
            return None

        if data.get("balance") is None:
            data["balance"] = 0

        if data.get("role") is None:
            data["role"] = UserRole.P
        if isinstance(data.get("role"), UserRole):
            data["role"] = data["role"].value

        # 3) UPSERT в user по FK telegram_info_id
        ins = pg_insert(User).values(telegram_id=telegram_info_id, **data)

        stmt = (
            ins.on_conflict_do_update(
                index_elements=["telegram_id"],
                set_={
                    "first_name": ins.excluded.first_name,
                    "last_name": ins.excluded.last_name,
                    "photo_id": ins.excluded.photo_id,
                    "balance": ins.excluded.balance,
                    "role": ins.excluded.role,
                    "longitude": ins.excluded.longitude,
                    "latitude": ins.excluded.latitude,
                },
            )
            .returning(
                User.id, User.telegram_id, User.first_name, User.last_name,
                User.photo_id, User.balance, User.role, User.longitude, User.latitude
            )
        )

        compiled = stmt.compile(
            dialect=postgresql.asyncpg.dialect(),
            compile_kwargs={"render_postcompile": True},
        )

        row = await self.database.fetchrow(str(compiled), *compiled.params.values())
        if row is None:
            return None

        return UserRead.model_validate(dict(row), from_attributes=True)