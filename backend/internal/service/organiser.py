from internal.repository.user import UserRepository
from internal.repository.photo import PhotoRepository
from internal.repository.event import EventRepository
import aiohttp
import base64

from internal.entity.base import EventCreate, UserRole, GetEvents, GetEvent, EventRead, EventUpdate, UpdateRequest, UserCreate, CategoryBase

from aiogram import Bot, types
import asyncio

from typing import List

class OrganiserService:
    def __init__(self, user_repo: UserRepository, photo_repo: PhotoRepository, event_repo: EventRepository):
        self.user_repo = user_repo
        self.photo_repo = photo_repo
        self.event_repo = event_repo
    

    async def create_event(self, event_create: EventCreate, bot: Bot) -> int | None:
        user = await self.user_repo.get_user_by_telegram_id(telegram_id=event_create.organiser_id)
        if user is None:
            print("Failed to get user", flush=True)
            return None
        
        if user.role != UserRole.ORGANISER:
            print("User is not organiser", flush=True)
            return None
        
        print(event_create.photo_ids)

        photo_ids = await self.photo_repo.create_photos(event_create.photo_ids)

        if photo_ids is None:
            print("failed to insert photo", flush=True)
            return None
        event_create.organiser_id = user.id
        event_id = await self.event_repo.create_event(event_create, photo_ids)

        if event_id is None:
            print("Failed to create event", flush=True)
            return None
        
        url = f"https://api.telegram.org/bot{bot.token}/getFile?file_id={event_create.photo_ids[0].url}"

        result = None

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"Response from Telegram API: {data}", flush=True)
                        result = data.get("result", None)
                    else:
                        print(f"Telegram API error: {response.status}", flush=True)
            except Exception as e:
                print(f"Failed to make request to Telegram API: {e}", flush=True)
        
        if result is None:
            return event_id

        file_path = result.get("file_path", None)

        if file_path is None:
            return event_id
        

        download_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
        image_bytes = None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        print(f"Image downloaded successfully, size: {len(image_bytes)} bytes", flush=True)
                    else:
                        print(f"Failed to download image: {response.status}", flush=True)
        except Exception as e:
            print(f"Failed to download image: {e}", flush=True)
        
        event_class = await self.send_to_classifier(
            classifier_service_url="http://classifier:8000/api/v1/predict",
            text=event_create.description,
            image_bytes=image_bytes
        )

        print("Class: ", event_class, flush=True)

        if event_class is None:
            print("Failed to get event class", flush=True)
            raise ValueError("Failed to get event class")
            return event_id
            event_class = "sportmisis"

        distributors = await self.user_repo.get_distributors(team_name=event_class)

        print(distributors)
        distributor_tg_ids = [d.telegram_id for d in distributors]
        await self.send_to_all_distributors(distributor_tg_ids=distributor_tg_ids, event_create=event_create, bot=bot)
        # for d in distributors:
        #     await self.send_to_distibutor(distributor_tg_id=d.telegram_id, event_create=event_create, bot_token=bot_token)

        return event_id
    
    async def send_to_distibutor(self, distributor_tg_id: int, event_create: EventCreate, bot: Bot) -> None:
        details_text = self.format_event_details(event=event_create)
        print("SEND TO ID: ", distributor_tg_id, flush=True)
        try:
            if event_create.photo_ids:
                print("PHOTO TO SEND URL: ", event_create.photo_ids[0].url, flush=True)
                media = [types.InputMediaPhoto(media=event_create.photo_ids[0].url, caption=details_text, parse_mode="Markdown")]
                await bot.send_media_group(
                    chat_id=distributor_tg_id,
                    media=media,
                )
            else:
                await bot.send_message(
                    chat_id=distributor_tg_id,
                    text=details_text,
                    parse_mode="Markdown",
                )
        except Exception as e:
            print(f"Error in send_to_distibutor: {e}", flush=True)

    async def send_to_all_distributors(self, distributor_tg_ids: List[int], event_create: EventCreate, bot: Bot) -> None:
        """
        Отправить сообщение всем дистрибьюторам с задержками
        для избежания flood control
        """
        successful = 0
        failed = 0

        for i, distributor_id in enumerate(distributor_tg_ids):
            print(f"Отправка {i+1}/{len(distributor_tg_ids)} дистрибьютору {distributor_id}", flush=True)
            
            try:
                await self.send_to_distibutor(distributor_id, event_create, bot)
                successful += 1
                
                # Добавляем задержку между сообщениями (не отправлять слишком быстро)
                if i < len(distributor_tg_ids) - 1:  # Не ждать после последнего
                    await asyncio.sleep(1)  # 1 секунда между сообщениями
                    
            except Exception as e:
                print(f"❌ Не удалось отправить дистрибьютору {distributor_id}: {e}", flush=True)
                failed += 1
                # При серьезной ошибке делаем большую паузу
                await asyncio.sleep(5)

        print(f"📊 Итог отправки: {successful} успешно, {failed} с ошибками", flush=True)

    def format_event_details(self, event: EventCreate) -> str:
        """Форматирует детальную информацию о мероприятии"""
        # Форматируем дату
        date_str = "Не указана"
        event_date = event.date
        date_str = event_date.strftime("%d.%m.%Y %H:%M")
        
        # Форматируем координаты
        coords_str = ""
        longitude = event.longitude
        latitude = event.latitude
        if longitude and latitude:
            coords_str = f"{latitude}, {longitude}"
        
        details = [
            f"📋 *Детали мероприятия*\n",
            f"*🏷 Название:* {event.name}",
            f"*📝 Описание:* {event.description}",
            f"*📅 Дата и время:* {date_str}",
            f"*📍 Место проведения:* {event.address}",
            f"*🗺 Координаты:* {coords_str}" if coords_str else "",
            f"*👥 Макс. участников:* {event.max_participants if event.max_participants > 0 else "Не ограничено"}",
            f"*🎂 Ограничение по возрасту:* {str(event.age_restriction) + "+" if event.max_participants > 0 else "Нет ограничений"}",
            f"*🔗 Ссылка на чат:* {event.chat_link}",
        ]
        
        # Убираем пустые строки
        details = [d for d in details if d]
        return "\n".join(details)



    async def send_to_classifier(self, classifier_service_url: str, text: str, image_bytes: bytes) -> str:
        """
        Отправляет картинку и текст на сервис классификации
        """
        try:
            # Кодируем картинку в base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Подготавливаем данные для отправки
            payload = {
                "text": text,
                "image": image_base64
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    classifier_service_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"Classifier response: {result}", flush=True)
                        
                        if result.get("success"):
                            predicted_class = result.get("predicted_class")
                            confidence = result.get("conf")
                            print(f"Predicted class: {predicted_class}, confidence: {confidence}", flush=True)
                            return predicted_class
                            
                            # Здесь можно сохранить результат предсказания в БД
                            # await self.save_prediction_result(event_id, predicted_class, confidence)
                        else:
                            print(f"Classifier returned error: {result}", flush=True)
                    else:
                        error_text = await response.text()
                        print(f"Classifier API error {response.status}: {error_text}", flush=True)
                        
        except aiohttp.ClientError as e:
            print(f"Network error when calling classifier: {e}", flush=True)
        except Exception as e:
            print(f"Error in send_to_classifier: {e}", flush=True)


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

    async def register_user(self, User2: UserCreate):
        user = await self.user_repo.create_user(user_create=User2)

        print("Serv user registr good", flush=True)
        if user is None:
            print("Failed to registr user", flush=True)
            return None
        return user

    async def add_category_to_user(self, category2: CategoryBase, token: int):
        user = await self.user_repo.add_category_to_user(user_id=int(token), category_in=category2)
        print("Serv user registr good", flush=True)
        if user is None:
            print("Failed to registr user", flush=True)
            return None
        return user

    async def get_recomend_post(self, token: int):
        user = await self.user_repo.get_recomend_post(user_id=int(token))
        print("Serv user registr good", flush=True)
        if user is None:
            print("Failed to registr user", flush=True)
            return None
        return user

