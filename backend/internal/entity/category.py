from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class CategoryBase(BaseSchema):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: Optional[str] = None


class CategoryRead(CategoryBase):
    id: int


class EventCategoryBase(BaseSchema):
    event_id: int
    category_id: int


class EventCategoryCreate(EventCategoryBase):
    pass


class EventCategoryRead(EventCategoryBase):
    pass


class UserCategoryBase(BaseSchema):
    user_id: int
    category_id: int


class UserCategoryCreate(UserCategoryBase):
    pass


class UserCategoryRead(UserCategoryBase):
    pass