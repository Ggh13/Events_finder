from internal.repository.user import UserRepository
from internal.repository.photo import PhotoRepository
from internal.repository.event import EventRepository

from internal.entity.base import EventCreate, UserRole, GetEvents, GetEvent, EventRead, EventUpdate, UpdateRequest, UserCreate

class OrganiserService:
    def __init__(self, user_repo: UserRepository, photo_repo: PhotoRepository, event_repo: EventRepository):
        self.user_repo = user_repo
        self.photo_repo = photo_repo
        self.event_repo = event_repo
    

    async def create_event(self, event_create: EventCreate) -> int | None:
        user = await self.user_repo.get_user_by_telegram_id(telegram_id=event_create.organiser_id)
        if user is None:
            print("Failed to get user", flush=True)
            return None
        
        if user.role != UserRole.ORGANISER:
            print("User is not organiser", flush=True)
            return None

        photo_ids = await self.photo_repo.create_photos(event_create.photo_ids)

        if photo_ids is None:
            print("failed to insert photo", flush=True)
            return None
        event_create.organiser_id = user.id
        event_id = await self.event_repo.create_event(event_create, photo_ids)

        if event_id is None:
            print("Failed to create event", flush=True)
            return None

        return event_id
    

    async def get_all_events(self, get_events: GetEvents):
        user = await self.user_repo.get_user_by_telegram_id(telegram_id=get_events.telegram_id)
        if user is None:
            print("Failed to get user", flush=True)
            return (None, None)
        
        if user.role != UserRole.ORGANISER:
            print("User is not organiser", flush=True)
            return (None, None)
        
        limit = 3
        offset = (get_events.page - 1) * limit
        (total_cnt, events) = await self.event_repo.get_events_by_user_paginated(user_id=user.id, limit=limit, offset=offset)
        
        if events is None:
            print("Failed to get events", flush=True)
            return (None, None)
        
        return (total_cnt, events)
    

    async def delete_event(self, telegram_id: int, event_id: int) -> int | None:
        user = await self.user_repo.get_user_by_telegram_id(telegram_id=telegram_id)
        if user is None:
            print("Failed to get user", flush=True)
            return None
        
        if user.role != UserRole.ORGANISER:
            print("User is not organiser", flush=True)
            return None
        
        event: EventRead = await self.event_repo.get_event_by_id(event_id=event_id)

        if event.organiser_id != user.id:
            print("User is not organiser of event", flush=True)
            return None
        
        if event is None:
            print("Failed to get event", flush=True)
            return None
        
        e_id = await self.event_repo.delete_event_by_id_compact(event_id=event_id)

        if e_id is None:
            print("Failed to delete event", flush=True)
            return None
        
        return e_id
    

    async def update_event(self, upd: UpdateRequest) -> int | None:
        user = await self.user_repo.get_user_by_telegram_id(telegram_id=upd.telegram_id)
        if user is None:
            print("Failed to get user", flush=True)
            return None
        
        if user.role != UserRole.ORGANISER:
            print("User is not organiser", flush=True)
            return None
        
        event: EventRead = await self.event_repo.get_event_by_id(event_id=upd.event_id)

        if event.organiser_id != user.id:
            print("User is not organiser of event", flush=True)
            return None
        
        if event is None:
            print("Failed to get event", flush=True)
            return None
        
        e_id = await self.event_repo.update_event_compact(event_update=upd)

        if e_id is None:
            print("Failed to delete event", flush=True)
            return None
        
        return e_id


    async def get_event(self, telegram_id: int, event_id: int):
        user = await self.user_repo.get_user_by_telegram_id(telegram_id=telegram_id)
        if user is None:
            print("Failed to get user", flush=True)
            return None
        
        if user.role != UserRole.ORGANISER:
            print("User is not organiser", flush=True)
            return None
        
        event: EventRead = await self.event_repo.get_event_by_id(event_id=event_id)

        if event.organiser_id != user.id:
            print("User is not organiser of event", flush=True)
            return None
        
        if event is None:
            print("Failed to get events", flush=True)
            return None
        
        return event

    async def register_user(self, User: UserCreate):
        user = await self.user_repo.create_user(user_create=User)
        print("Serv user registr good", flush=True)
        if user is None:
            print("Failed to registr user", flush=True)
            return None
        return user

