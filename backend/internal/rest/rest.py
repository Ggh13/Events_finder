from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from typing import List
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

from internal.service.organiser import OrganiserService

from internal.entity.base import EventCreate, GetEvents, EventRead, UpdateRequest, GetAllEvents, UserRegisterRequest, UserRead,UserCreate, RegisterResponse, CategoryBase
from fastapi import Depends

from pkg.logger.logger import Logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()
class RouterConfig(BaseSettings):
    host: str = Field(..., alias="REST_HOST")
    port: int = Field(5432, alias="REST_PORT")
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REST_"
        case_sensitive = False
        extra="allow"

    
class Router:
    def __init__(self, cfg: RouterConfig, organiser_service: OrganiserService):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.config = uvicorn.Config(
            self.app,
            host=cfg.host,
            port=cfg.port,
            log_level="info"
        )
        self.organiser_service = organiser_service
        self.server = uvicorn.Server(self.config)
        
        @self.app.get("/")
        async def root():
            return {"message": "Hello World"}

        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}

        @self.app.get("/api")
        async def root():
            return {"message": "Hello World"}

        @self.app.get("/api/health")
        async def health():
            return {"status": "healthy"}
        
        @self.app.post("/api/create_event")
        async def create_event(event: EventCreate):
            event_id = await self.organiser_service.create_event(event)
            if event_id is None:
                raise HTTPException(
                    status_code=500,
                    detail="failed to create event"
                )
            return {"event_id": event_id}
        
        @self.app.get("/api/get_events", response_model=GetAllEvents)
        async def get_events(get_events: GetEvents):
            print("Req:", get_events, flush=True)
            (total_cnt, events) = await self.organiser_service.get_all_events(get_events)
            if events is None:
                raise HTTPException(
                    status_code=500,
                    detail="failed to list events"
                )
            print("*****************************", flush=True)
            print(events, flush =True)
            
            return GetAllEvents(
                total_cnt=total_cnt,
                events=events
            )
        
        @self.app.get("/api/get_event/", response_model=EventRead)
        async def get_event(telegram_id: int, event_id: int):
            event = await self.organiser_service.get_event(telegram_id=telegram_id, event_id=event_id)
            if event is None:
                raise HTTPException(
                    status_code=500,
                    detail="failed to get event"
                )
            print("*****************************", flush=True)
            print(event, flush =True)
            
            return event
        
        @self.app.delete("/api/delete_event/")
        async def delete_event(telegram_id: int, event_id: int):
            event_id = await self.organiser_service.delete_event(telegram_id=telegram_id, event_id=event_id)
            if event_id is None:
                raise HTTPException(
                    status_code=500,
                    detail="failed to delete event"
                )
            return {
                "event_id": event_id
            }
        
        @self.app.post("/api/register", response_model=RegisterResponse)
        async def register_user_endpoint(payload: UserRegisterRequest):

            user = await organiser_service.register_user(payload.user)
            if user is None:
                raise HTTPException(status_code=404, detail="telegram_id not found in telegram_info")
            return {"user" : user,
                    "comment" : "??"}


        
        @self.app.post("/api/add_category", response_model=RegisterResponse)
        async def register_user_endpoint(
            payload: CategoryBase,
            credentials: HTTPAuthorizationCredentials = Depends(security),
        ):
            token = credentials.credentials  # <-- это сам Bearer-токен
            user = await organiser_service.add_category_to_user(payload, token)
            if isinstance(user, str):
                return {"user" : 333,
                    "comment" : str(e)}
            if user is None:
                raise HTTPException(status_code=404, detail="telegram_id not found in telegram_info")
            return {"user" : user,
                    "comment" : "??"}
        
    async def run(self):
        await self.server.serve()