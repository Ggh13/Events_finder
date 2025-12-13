from aiogram import Router, types, F
from aiogram.filters import Command
import aiohttp

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, Any

from datetime import datetime


router = Router(name=__name__)


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


@router.message(Command("create_event"))
async def handle_create_event(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введите название нового мероприятия"
    )
    await state.set_state(EventCreation.name)


@router.message(EventCreation.name)
async def proccess_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="Введите описание мероприятия"
    )
    await state.set_state(EventCreation.description)


@router.message(EventCreation.description)
async def proccess_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        text="Введите дату и время мероприятия в формате 2021-02-01T15:30"
    )
    await state.set_state(EventCreation.date)


@router.message(EventCreation.date)
async def proccess_date(message: types.Message, state: FSMContext):
    await state.update_data(date=datetime.fromisoformat(message.text))
    await message.answer(
        text="Введите полный адрес, где будет проходить мероприятие. Лучше зайдите на Яндекс карты"
    )
    await state.set_state(EventCreation.location)


@router.message(EventCreation.location)
async def proccess_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer(
        text="Введите координаты места проведения. Их можно скопировать на Яндекс картах"
    )
    await state.set_state(EventCreation.coords)


@router.message(EventCreation.coords)
async def proccess_coords(message: types.Message, state: FSMContext):
    await state.update_data(coords=message.text)
    await message.answer(
        text="Введите максимальное количество участников мероприятия"
    )
    await state.set_state(EventCreation.max_participants)


@router.message(EventCreation.max_participants)
async def proccess_max_participants(message: types.Message, state: FSMContext):
    await state.update_data(max_participants=int(message.text))
    await message.answer(
        text="Введите ограничение по возрасту (одно число - возраст)"
    )
    await state.set_state(EventCreation.age_restriction)

@router.message(EventCreation.age_restriction)
async def proccess_age_restriction(message: types.Message, state: FSMContext):
    await state.update_data(age_restriction=int(message.text))
    await message.answer(
        text="Отправьте одним сообщением фото для мероприятия (максимум 3)"
    )
    await state.set_state(EventCreation.photos)

@router.message(EventCreation.photos, content_types=[types.ContentType.PHOTO])
async def proccess_age_restriction(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        photos = data.get('photos', [])
        if message.photo:
            if len(message.photo) > 1:
                for photo in message.photo(max(3, len(message.photo))):
                    photo_data = await process_single_photo(photo)
                    photos.append(photo_data)
            else:
                photo = message.photo[-1]
                photo_data = await process_single_photo(photo)
                photos.append(photo_data)
            
            data['photos'] = photos


async def process_single_photo(photo: types.PhotoSize) -> Dict:
    """Скачивает и обрабатывает одно фото"""
    photo_file = await bot.download_file_by_id(photo.file_id)
    photo_bytes = photo_file.read()
    
    return {
        'bytes': photo_bytes,
        'file_id': photo.file_id,
        'file_unique_id': photo.file_unique_id,
        'width': photo.width,
        'height': photo.height,
        'file_size': photo.file_size
    }

            
async def show_summary(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    confirmation_text = (
        "📋 *Проверьте данные мероприятия:*\n\n"
        f"*🏷 Название:* {data['name']}\n"
        f"*📝 Описание:* {data['description']}\n"
        f"*📅 Дата:* {data['date']}\n"
        f"*📍 Место:* {data['location']}\n"
        f"*👥 Макс. участников:* {data['max_participants']}\n"
        f"*👥 Возрастное ограничение:* {data['age_restriction']}\n"
    )
    await message.answer(confirmation_text, parse_mode="Markdown")


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
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


@router.message(Command("edit_event"))
async def handle_create_event(message: types.Message):
    await message.answer(
        text="Edit event"
    )


@router.message(Command("delete_event"))
async def handle_create_event(message: types.Message):
    await message.answer(
        text="Delete event"
    )


@router.message(Command("created_events"))
async def handle_create_event(message: types.Message):
    await message.answer(
        text="Created event"
    )