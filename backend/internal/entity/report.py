from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


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
    sender: Optional["UserRead"] = None
    reported_user: Optional["UserRead"] = None


class EventReportBase(ReportBase):
    reported_event_id: int


class EventReportCreate(EventReportBase):
    sender_id: int


class EventReportRead(EventReportBase):
    id: uuid.UUID
    sender_id: int
    

class EventReportWithRelations(EventReportRead):
    sender: Optional["UserRead"] = None
    reported_event: Optional["EventRead"] = None


EventReportWithRelations.model_rebuild()
UserReportWithRelations.model_rebuild()