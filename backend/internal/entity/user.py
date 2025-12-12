from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class UserRole(str, Enum):
    PARTICIPANT = 'P'
    ADMIN = 'A'
    ORGANISER = 'O'
    DISTRIBUTOR = 'D'


class TicketStatus(str, Enum):
    PENDING = 'P'
    ACCEPTED = 'A'
    DELETED = 'D'


class PhotoRead(PhotoBase):
    id: int


class TelegramInfoBase(BaseSchema):
    telegram_id: int
    username: str
    chat_id: int


class TelegramInfoCreate(TelegramInfoBase):
    pass


class TelegramInfoUpdate(BaseSchema):
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    chat_id: Optional[int] = None


class TelegramInfoRead(TelegramInfoBase):
    id: int


class UserBase(BaseSchema):
    first_name: str
    last_name: str
    balance: int = Field(ge=0)
    role: UserRole = UserRole.PARTICIPANT
    longitude: float
    latitude: float


class UserCreate(UserBase):
    telegram_info: Optional["TelegramInfoCreate"] = None
    photo_id: Optional[int] = None


class UserUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_id: Optional[int] = None
    balance: Optional[int] = Field(None, ge=0)
    role: Optional[UserRole] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class UserRead(UserBase):
    id: int
    telegram_id: Optional[int] = None
    photo_id: Optional[int] = None


class UserWithRelations(UserRead):
    telegram_info: Optional["TelegramInfoRead"] = None
    photo: Optional["PhotoRead"] = None
    teams: List["TeamRead"] = []
    categories: List["CategoryRead"] = []


class UserTeamBase(BaseSchema):
    user_id: int
    team_id: int


class UserTeamCreate(UserTeamBase):
    pass


class UserTeamRead(UserTeamBase):
    pass


class UserFilter(BaseSchema):
    role: Optional[UserRole] = None
    min_balance: Optional[int] = None
    max_balance: Optional[int] = None
    category_ids: Optional[List[int]] = None


class EventFilter(BaseSchema):
    organiser_id: Optional[int] = None
    category_ids: Optional[List[int]] = None
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None
    min_age_restriction: Optional[int] = None
    max_age_restriction: Optional[int] = None
    min_cost: Optional[int] = None
    max_cost: Optional[int] = None
    is_freezed: Optional[bool] = None
    search_text: Optional[str] = None


class TicketFilter(BaseSchema):
    user_id: Optional[int] = None
    event_id: Optional[int] = None
    status: Optional[TicketStatus] = None
    min_created_at: Optional[datetime] = None
    max_created_at: Optional[datetime] = None


class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    

UserWithRelations.model_rebuild()




