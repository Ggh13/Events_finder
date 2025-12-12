from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class TeamBase(BaseSchema):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseSchema):
    name: Optional[str] = None

class TeamRead(TeamBase):
    id: int

class TeamWithUsers(TeamRead):
    users: List["UserRead"] = []


TeamWithUsers.model_rebuild()