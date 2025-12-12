from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    DECIMAL, ForeignKey, UniqueConstraint, CheckConstraint,
    Enum, BigInteger, UUID
)
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum



Base = declarative_base()


from sqlalchemy import event
from sqlalchemy.schema import CreateSchema

event.listen(Base.metadata, 'before_create', CreateSchema('events_finder'))

class UserRole(str, enum.Enum):
    PARTICIPANT = 'P'
    ADMIN = 'A'
    ORGANISER = 'O'
    DISTRIBUTOR = 'D'


class TicketStatus(str, enum.Enum):
    PENDING = 'P'
    ACCEPTED = 'A'
    DELETED = 'D'


class Photo(Base):
    __tablename__ = 'photo'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, default='')
    
    user = relationship("User", back_populates="photo_rel")
    events = relationship("Event", secondary="events_finder.event_photo", back_populates="photos")


class TelegramInfo(Base):
    __tablename__ = 'telegram_info'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text, unique=True, nullable=False)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    
    user = relationship("User", back_populates="telegram_info_rel", uselist=False)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, ForeignKey('events_finder.telegram_info.id'))
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    photo_id = Column(Integer, ForeignKey('events_finder.photo.id'))
    balance = Column(Integer, nullable=False)
    role = Column(
        PG_ENUM(UserRole, name='user_role', create_type=False),
        nullable=False,
        default=UserRole.PARTICIPANT
    )
    longitude = Column(DECIMAL(8, 6), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)
    
    telegram_info_rel = relationship("TelegramInfo", back_populates="user")
    photo_rel = relationship("Photo", back_populates="user")
    teams = relationship("Team", secondary="events_finder.user_team", back_populates="users")
    categories = relationship("Category", secondary="events_finder.user_category", back_populates="users")
    organized_events = relationship("Event", back_populates="organiser")
    tickets = relationship("Ticket", back_populates="user")
    
    banned_users = relationship(
        "User",
        secondary="events_finder.user_ban",
        primaryjoin="User.id == UserBan.user_id",
        secondaryjoin="User.id == UserBan.user_ban_id",
        backref="banned_by"
    )
    
    sent_reports = relationship("UserReport", foreign_keys="UserReport.sender_id", back_populates="sender")
    received_reports = relationship("UserReport", foreign_keys="UserReport.reported_user_id", back_populates="reported_user")
    
    event_reports_sent = relationship("EventReport", foreign_keys="EventReport.sender_id", back_populates="sender")


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    
    users = relationship("User", secondary="events_finder.user_team", back_populates="teams")


class UserTeam(Base):
    __tablename__ = 'user_team'
    __table_args__ = (
        # Словарь как первый элемент
        UniqueConstraint('user_id', 'team_id'),
        {'schema': 'events_finder'},  
        # Другие constraints если нужно
    )
    
    user_id = Column(Integer, ForeignKey('events_finder.user.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('events_finder.team.id'), primary_key=True)


class Category(Base):
    __tablename__ = 'category'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    
    users = relationship("User", secondary="events_finder.user_category", back_populates="categories")
    events = relationship("Event", secondary="events_finder.event_category", back_populates="categories")


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    address = Column(Text, nullable=False)
    longitude = Column(DECIMAL(8, 6), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)
    age_restriction = Column(Integer, nullable=False)
    chat_link = Column(Text, nullable=False)
    organiser_id = Column(Integer, ForeignKey('events_finder.user.id'))
    max_participants = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    balance = Column(Integer, nullable=False)
    is_freezed = Column(Boolean, nullable=False, default=False)
    
    organiser = relationship("User", back_populates="organized_events")
    categories = relationship("Category", secondary="events_finder.event_category", back_populates="events")
    photos = relationship("Photo", secondary="events_finder.event_photo", back_populates="events")
    tickets = relationship("Ticket", back_populates="event")
    
    reports = relationship("EventReport", back_populates="reported_event")


class EventPhoto(Base):
    __tablename__ = 'event_photo'
    __table_args__ = (
        UniqueConstraint('event_id', 'photo_id'),
        {'schema': 'events_finder'},
        
    )
    
    event_id = Column(Integer, ForeignKey('events_finder.event.id'), primary_key=True)
    photo_id = Column(Integer, ForeignKey('events_finder.photo.id'), primary_key=True)


class EventCategory(Base):
    __tablename__ = 'event_category'
    __table_args__ = (
        UniqueConstraint('event_id', 'category_id'),
        {'schema': 'events_finder'},
        
    )
    
    event_id = Column(Integer, ForeignKey('events_finder.event.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('events_finder.category.id'), primary_key=True)


class UserCategory(Base):
    __tablename__ = 'user_category'
    __table_args__ = (
        UniqueConstraint('user_id', 'category_id'),
        {'schema': 'events_finder'},
        
    )
    
    user_id = Column(Integer, ForeignKey('events_finder.user.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('events_finder.category.id'), primary_key=True)


class Ticket(Base):
    __tablename__ = 'ticket'
    __table_args__ = (
        UniqueConstraint('user_id', 'event_id'),
        {'schema': 'events_finder'},
        
    )
    
    id = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey('events_finder.user.id'))
    event_id = Column(Integer, ForeignKey('events_finder.event.id'))
    status = Column(
        PG_ENUM(TicketStatus, name='ticket_status', create_type=False),
        nullable=False,
        default=TicketStatus.PENDING
    )
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")


class UserBan(Base):
    __tablename__ = 'user_ban'
    __table_args__ = (
        UniqueConstraint('user_id', 'user_ban_id'),
        {'schema': 'events_finder'},
        
    )
    
    user_id = Column(Integer, ForeignKey('events_finder.user.id'), primary_key=True)
    user_ban_id = Column(Integer, ForeignKey('events_finder.user.id'), primary_key=True)


class UserReport(Base):
    __tablename__ = 'user_report'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(UUID, primary_key=True)
    sender_id = Column(Integer, ForeignKey('events_finder.user.id'))
    message = Column(Text, nullable=False)
    reported_user_id = Column(Integer, ForeignKey('events_finder.user.id'))
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_reports")
    reported_user = relationship("User", foreign_keys=[reported_user_id], back_populates="received_reports")


class EventReport(Base):
    __tablename__ = 'event_report'
    __table_args__ = ({'schema': 'events_finder'},)
    
    id = Column(UUID, primary_key=True)
    sender_id = Column(Integer, ForeignKey('events_finder.user.id'))
    message = Column(Text, nullable=False)
    reported_event_id = Column(Integer, ForeignKey('events_finder.event.id'))
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="event_reports_sent")
    reported_event = relationship("Event", back_populates="reports")