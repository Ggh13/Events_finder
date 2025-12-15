from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

# Enums
class UserRole(str, Enum):
    PARTICIPANT = 'PARTICIPANT'
    ADMIN = 'ADMIN'
    ORGANISER = 'ORGANISER'
    DISTRIBUTOR = 'DISTRIBUTOR'

class TicketStatus(str, Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DELETED = 'DELETED'

# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Photo schemas
class PhotoBase(BaseSchema):
    url: str = Field(default="")

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(PhotoBase):
    pass

class PhotoRead(PhotoBase):
    id: int

# TelegramInfo schemas
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

# User schemas
class UserBase(BaseSchema):
    first_name: str
    last_name: str
    balance: int = Field(ge=0)
    role: UserRole = UserRole.PARTICIPANT
    longitude: float
    latitude: float

class UserCreate(UserBase):
    telegram_info: Optional[TelegramInfoRead] = None
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
    telegram_info: Optional[TelegramInfoRead] = None
    photo: Optional[PhotoRead] = None
    teams: List["TeamRead"] = []
    categories: List["CategoryRead"] = []

# Team schemas
class TeamBase(BaseSchema):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseSchema):
    name: Optional[str] = None

class TeamRead(TeamBase):
    id: int

class TeamWithUsers(TeamRead):
    users: List[UserRead] = []

# Category schemas
class CategoryBase(BaseSchema):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseSchema):
    name: Optional[str] = None

class CategoryRead(CategoryBase):
    id: int


class GetEvents(BaseModel):
    telegram_id: int
    page: int
    
    
class GetEvent(BaseModel):
    telegram_id: int
    event_id: int
    

# Event schemas
class EventBase(BaseSchema):
    name: str
    description: str
    date: datetime
    address: str
    longitude: float
    latitude: float
    age_restriction: int = Field(ge=0, le=120)
    chat_link: str
    max_participants: int = Field(gt=0)
    cost: int = Field(ge=0)
    balance: int = Field(ge=0)
    is_freezed: bool = False

class EventCreate(EventBase):
    organiser_id: int
    category_ids: Optional[List[int]] = []
    photo_ids: Optional[List[PhotoCreate]] = []

class EventUpdate(BaseSchema):
    event_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    age_restriction: Optional[int] = Field(None, ge=0, le=120)
    chat_link: Optional[str] = None
    max_participants: Optional[int] = Field(None, gt=0)
    cost: Optional[int] = Field(None, ge=0)
    balance: Optional[int] = Field(None, ge=0)
    is_freezed: Optional[bool] = None
    organiser_id: Optional[int] = None

class UpdateRequest(EventUpdate):
    telegram_id: int

class EventRead(EventBase):
    id: int
    organiser_id: int
    photo_ids: Optional[List[PhotoCreate]] = []
    category_ids: Optional[List[int]] = []

class GetAllEvents(BaseModel):
    total_cnt: int
    events: Optional[List[EventRead]]

class EventWithRelations(EventRead):
    organiser: Optional[UserRead] = None
    categories: List[CategoryRead] = []
    photos: List[PhotoRead] = []
    tickets: List["TicketRead"] = []

# Ticket schemas
class TicketBase(BaseSchema):
    status: TicketStatus = TicketStatus.PENDING

class TicketCreate(TicketBase):
    user_id: int
    event_id: int

class TicketUpdate(BaseSchema):
    status: Optional[TicketStatus] = None

class TicketRead(TicketBase):
    id: uuid.UUID
    user_id: int
    event_id: int
    created_at: datetime
    updated_at: datetime

class TicketWithRelations(TicketRead):
    user: Optional[UserRead] = None
    event: Optional[EventRead] = None

# UserTeam schemas
class UserTeamBase(BaseSchema):
    user_id: int
    team_id: int

class UserTeamCreate(UserTeamBase):
    pass

class UserTeamRead(UserTeamBase):
    pass

# EventPhoto schemas
class EventPhotoBase(BaseSchema):
    event_id: int
    photo_id: int

class EventPhotoCreate(EventPhotoBase):
    pass

class EventPhotoRead(EventPhotoBase):
    pass

# EventCategory schemas
class EventCategoryBase(BaseSchema):
    event_id: int
    category_id: int

class EventCategoryCreate(EventCategoryBase):
    pass

class EventCategoryRead(EventCategoryBase):
    pass

# UserCategory schemas
class UserCategoryBase(BaseSchema):
    user_id: int
    category_id: int

class UserCategoryCreate(UserCategoryBase):
    pass

class UserCategoryRead(UserCategoryBase):
    pass

# UserBan schemas
class UserBanBase(BaseSchema):
    user_id: int
    user_ban_id: int

class UserBanCreate(UserBanBase):
    pass

class UserBanRead(UserBanBase):
    pass

# Report schemas
class ReportBase(BaseSchema):
    message: str

class UserReportBase(ReportBase):
    reported_user_id: int

class UserReportCreate(UserReportBase):
    sender_id: int

class UserReportRead(UserReportBase):
    id: uuid.UUID
    sender_id: int

class UserReportWithRelations(UserReportRead):
    sender: Optional[UserRead] = None
    reported_user: Optional[UserRead] = None

class EventReportBase(ReportBase):
    reported_event_id: int

class EventReportCreate(EventReportBase):
    sender_id: int

class EventReportRead(EventReportBase):
    id: uuid.UUID
    sender_id: int

class EventReportWithRelations(EventReportRead):
    sender: Optional[UserRead] = None
    reported_event: Optional[EventRead] = None

# Filter schemas
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

# Response schemas
class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Update forward references
UserWithRelations.model_rebuild()
TeamWithUsers.model_rebuild()
EventWithRelations.model_rebuild()
TicketWithRelations.model_rebuild()
UserReportWithRelations.model_rebuild()
EventReportWithRelations.model_rebuild()