from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum



class UserBanBase(BaseSchema):
    user_id: int
    user_ban_id: int


class UserBanCreate(UserBanBase):
    pass


class UserBanRead(UserBanBase):
    pass