from aiogram import Bot, Dispatcher, types
from pydantic_settings import BaseSettings
from pydantic import Field

from aiogram import Router, types, F
from aiogram.filters import Command
import aiohttp

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, Any

from datetime import datetime

from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import BaseMiddleware
import asyncio


class EventCreation(StatesGroup):
    name = State()
    description = State()
    date = State()
    location = State()
    coords = State()
    chat_link = State()
    max_participants = State()
    age_restriction = State()
    photos = State()

class Photos(StatesGroup):
    photos = State()

import logging

class BotConfig(BaseSettings):
    token: str = Field(..., alias="BOT_TOKEN")
    class Config:
        env_file = "./config/.env"
        env_file_encoding = "utf-8"
        env_prefix = "REST_"
        case_sensitive = False

class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency = 0.1):
        # Initialize latency and album_data dictionary
        self.latency = latency
        self.album_data = {}
#
    def collect_album_messages(self, event: types.Message):
        """
        Collect messages of the same media group.
        """
#         # Check if media_group_id exists in album_data
        if event.media_group_id not in self.album_data:
#             # Create a new entry for the media group
            self.album_data[event.media_group_id] = {"messages": []}
#
#         # Append the new message to the media group
        self.album_data[event.media_group_id]["messages"].append(event)
#
#         # Return the total number of messages in the current media group
        return len(self.album_data[event.media_group_id]["messages"])
#
    async def __call__(self, handler, event: types.Message, data: Dict[str, Any]) -> Any:
        """
        Main middleware logic.
        """
#         # If the event has no media_group_id, pass it to the handler immediately
        if not event.media_group_id:
            return await handler(event, data)
#
#         # Collect messages of the same media group
        total_before = self.collect_album_messages(event)
#
#         # Wait for a specified latency period
        await asyncio.sleep(self.latency)
#
#         # Check the total number of messages after the latency
        total_after = len(self.album_data[event.media_group_id]["messages"])
#
#         # If new messages were added during the latency, exit
        if total_before != total_after:
            return
#
#         # Sort the album messages by message_id and add to data
        album_messages = self.album_data[event.media_group_id]["messages"]
        album_messages.sort(key=lambda x: x.message_id)
        data["album"] = album_messages
#
        del self.album_data[event.media_group_id]
#         # Call the original event handler
        return await handler(event, data)

class TelegramBot:
    def __init__(self, cfg: BotConfig):
        self.token = cfg.token
        print(self.token)
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        
        logging.basicConfig(level=logging.INFO)


        @self.dp.message(Command("create_event"))
        async def handle_create_event(message: types.Message, state: FSMContext):
            await message.answer(
                text="Введите название нового мероприятия"
            )
            await state.set_state(EventCreation.name)


        @self.dp.message(EventCreation.name)
        async def proccess_name(message: types.Message, state: FSMContext):
            await state.update_data(name=message.text)
            await message.answer(
                text="Введите описание мероприятия"
            )
            await state.set_state(EventCreation.description)


        @self.dp.message(EventCreation.description)
        async def proccess_description(message: types.Message, state: FSMContext):
            await state.update_data(description=message.text)
            await message.answer(
                text="Введите дату и время мероприятия в формате 2021-02-01T15:30"
            )
            await state.set_state(EventCreation.date)


        @self.dp.message(EventCreation.date)
        async def proccess_date(message: types.Message, state: FSMContext):
            await state.update_data(date=datetime.fromisoformat(message.text))
            await message.answer(
                text="Введите полный адрес, где будет проходить мероприятие. Лучше зайдите на Яндекс карты"
            )
            await state.set_state(EventCreation.location)


        @self.dp.message(EventCreation.location)
        async def proccess_location(message: types.Message, state: FSMContext):
            await state.update_data(location=message.text)
            await message.answer(
                text="Введите координаты места проведения. Их можно скопировать на Яндекс картах"
            )
            await state.set_state(EventCreation.coords)


        @self.dp.message(EventCreation.coords)
        async def proccess_coords(message: types.Message, state: FSMContext):
            await state.update_data(coords=message.text)
            await message.answer(
                text="Введите максимальное количество участников мероприятия"
            )
            await state.set_state(EventCreation.max_participants)


        @self.dp.message(EventCreation.max_participants)
        async def proccess_max_participants(message: types.Message, state: FSMContext):
            await state.update_data(max_participants=int(message.text))
            await message.answer(
                text="Введите ограничение по возрасту (одно число - возраст)"
            )
            await state.set_state(EventCreation.age_restriction)


        @self.dp.message(EventCreation.age_restriction)
        async def proccess_age_restriction(message: types.Message, state: FSMContext):
            await state.update_data(age_restriction=int(message.text))
            await message.answer(
                text="Добавьте фото для вашего мероприятия"
            )
            await state.set_state(EventCreation.photos)


        @self.dp.message(EventCreation.photos)
        async def proccess_photos(message: types.Message, state: FSMContext):
            if not message.photo:
                return
            photos = []
            photo_size = message.photo[-1]
            file = await self.bot.get_file(photo_size.file_id)
            file_path = file.file_path

            photo_bytes = await self.bot.download_file(file_path)
            photo_data = photo_bytes.read() if hasattr(photo_bytes, 'read') else photo_bytes
            print(photo_size.file_id)
            photo_info = {
                'bytes': photo_data,
                'file_id': photo_size.file_id,
                'file_unique_id': photo_size.file_unique_id,
                'width': photo_size.width,
                'height': photo_size.height,
                'file_size': photo_size.file_size
            }
            
            photos.append(photo_info)
            await state.update_data(photos=photos)

            await show_summary(message=message, state=state)


        async def show_summary(message: types.Message, state: FSMContext) -> None:
            data = await state.get_data()
            photos = data.get('photos', [])
            
            # Отправляем текстовую информацию
            preview_text = create_preview_text(data)
            await message.answer(preview_text, parse_mode="Markdown")
            
            if photos:
                if len(photos) == 1:
                    # Отправка одного фото
                    await self.bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photos[0]['file_id'],
                        caption="📷 *Добавленное фото:*",
                        parse_mode="Markdown"
                    )
                else:
                    # Создание медиагруппы для нескольких фото
                    media_group = MediaGroupBuilder(caption="📷 *Добавленные фото:*")
                    
                    # Добавляем все фото в медиагруппу
                    for photo_data in photos:
                        media_group.add_photo(
                            media=photo_data['file_id']
                        )
                    
                    # Отправляем медиагруппу
                    await self.bot.send_media_group(
                        chat_id=message.chat.id,
                        media=media_group.build()
                    )

        @self.dp.message(Command("cancel"))
        @self.dp.message(F.text.casefold() == "cancel")
        async def cancel_handler(message: types.Message, state: FSMContext) -> None:
            """
            Отмена создания мероприятия
            """
            current_state = await state.get_state()
            if current_state is None:
                return

            await state.clear()
            await message.answer(
                "Cancelled.",
            )
        

        def create_preview_text(data: dict) -> str:
            """Создает текстовый предпросмотр всех данных"""
            photos_count = len(data.get('photos', []))
            
            text = (
                "📋 *Предпросмотр мероприятия:*\n\n"
                f"*🏷 Название:* {data['name']}\n"
                f"*📝 Описание:* {data['description']}\n"
                f"*📅 Дата и время:* {data['date']}\n"
                f"*📍 Место:* {data['location']}\n"
                f"*👥 Макс. участников:* {data['max_participants']}\n"
                f"*🖼 Фото:* {photos_count} шт.\n"
            )
            
            return text


        @self.dp.message(Command("edit_event"))
        async def handle_edit_event(message: types.Message):
            await message.answer(
                text="Edit event"
            )


        @self.dp.message(Command("delete_event"))
        async def handle_delete_event(message: types.Message):
            await message.answer(
                text="Delete event"
            )


        @self.dp.message(Command("created_events"))
        async def handle_created_events(message: types.Message):
            await message.answer(
            text="Created event"
        )

    async def run(self):
        await self.dp.start_polling(self.bot)
