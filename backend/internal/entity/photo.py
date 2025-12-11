from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class PhotoBase(BaseSchema):
    url: str = Field(default="")


class PhotoCreate(PhotoBase):
    pass


class PhotoUpdate(PhotoBase):
    pass


class PhotoRead(PhotoBase):
    id: int


class EventPhotoBase(BaseSchema):
    event_id: int
    photo_id: int

class EventPhotoCreate(EventPhotoBase):
    pass

class EventPhotoRead(EventPhotoBase):
    pass