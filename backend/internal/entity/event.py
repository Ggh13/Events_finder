from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


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
    photo_ids: Optional[List[int]] = []


class EventUpdate(BaseSchema):
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


class EventRead(EventBase):
    id: int
    organiser_id: int


class EventWithRelations(EventRead):
    organiser: Optional["UserRead"] = None
    categories: List["CategoryRead"] = []
    photos: List["PhotoRead"] = []
    tickets: List["TicketRead"] = []


class TicketBase(BaseSchema):
    status: TicketStatus = TicketStatus.PENDING


class TicketCreate(TicketBase):
    user_id: int
    event_id: int


class TicketUpdate(BaseSchema):
    status: Optional["TicketStatus"] = None


class TicketRead(TicketBase):
    id: uuid.UUID
    user_id: int
    event_id: int
    created_at: datetime
    updated_at: datetime


class TicketWithRelations(TicketRead):
    user: Optional["UserRead"] = None
    event: Optional["EventRead"] = None


TicketWithRelations.model_rebuild()

EventWithRelations.model_rebuild()