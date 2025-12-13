from aiogram import Router, types, F
from aiogram.filters import Command
import aiohttp

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, Any

from datetime import datetime


from aiogram.utils.media_group import MediaGroupBuilder
from internal.bot.categories import categories

router = Router(name=__name__)

cats = list(categories.keys())


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
    categories = State()
    confirmation = State()

    

@router.message(Command("create_event"))
async def handle_create_event(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введите название нового мероприятия"
    )
    await state.set_state(EventCreation.name)


@router.message(EventCreation.name)
async def proccess_name(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат названия. Введите заново"
        )
        return
    await state.update_data(name=message.text)
    await message.answer(
        text="Введите описание мероприятия"
    )
    await state.set_state(EventCreation.description)


@router.message(EventCreation.description)
async def proccess_description(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат описания. Введите заново"
        )
        return
    await state.update_data(description=message.text)
    await message.answer(
        text="Введите дату и время мероприятия в формате 2021-02-01T15:30"
    )
    await state.set_state(EventCreation.date)


@router.message(EventCreation.date)
async def proccess_date(message: types.Message, state: FSMContext):
    try:
        date = datetime.fromisoformat(message.text)
    except ValueError as e:
        await message.answer(
            "Неправильный формат даты. Введите заново"
        )
        return
    await state.update_data(date=date)
    await message.answer(
        text="Введите полный адрес, где будет проходить мероприятие. Лучше зайдите на Яндекс карты"
    )
    await state.set_state(EventCreation.location)


@router.message(EventCreation.location)
async def proccess_location(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат адреса. Введите заново"
        )
        return
    await state.update_data(location=message.text)
    await message.answer(
        text="Введите координаты места проведения. Их можно скопировать на Яндекс картах"
    )
    await state.set_state(EventCreation.coords)


@router.message(EventCreation.coords)
async def proccess_coords(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат координат. Введите заново"
        )
        return
    
    try:
        coords = list(map(float, message.text.split(", ")))
    except ValueError:
        await message.answer(
            "Неправильный формат координат. Введите заново"
        )
        return
    
    await state.update_data(coords=message.text)
    await message.answer(
        text="Введите ссылку на чат с участниками"
    )
    await state.set_state(EventCreation.chat_link)


@router.message(EventCreation.chat_link)
async def proccess_chat_link(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат ссылки. Введите заново"
        )
        return
    
    await state.update_data(chat_link=message.text)
    await message.answer(
        text="Введите максимальное количество участников мероприятия"
    )
    await state.set_state(EventCreation.max_participants)


@router.message(EventCreation.max_participants)
async def proccess_max_participants(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат количества. Введите заново"
        )
        return
    
    try:
        max_participants = int(message.text)
    except:
        await message.answer(
            "Неправильный формат количества. Введите заново"
        )
        return
    
    if max_participants < 0:
        await message.answer(
            "Неправильный формат количества. Введите заново"
        )
        return

    await state.update_data(max_participants=max_participants)
    await message.answer(
        text="Введите ограничение по возрасту (одно число - возраст)"
    )
    await state.set_state(EventCreation.age_restriction)


@router.message(EventCreation.age_restriction)
async def proccess_age_restriction(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат возраста. Введите заново"
        )
        return

    try:
        age_restriction = int(message.text)
    except:
        await message.answer(
            "Неправильный формат возраста. Введите заново"
        )
        return
    
    if age_restriction < 0 or age_restriction > 120:
        await message.answer(
            "Неправильный формат возраста. Введите заново"
        )
        return
    
    await state.update_data(age_restriction=age_restriction)
    await message.answer(
        text="Добавьте фото для вашего мероприятия"
    )
    await state.set_state(EventCreation.photos)


@router.message(EventCreation.photos)
async def proccess_photos(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            text="Нужно отправить фотографию"
        )
        return
    
    photo_size = message.photo[-1]
    photos = []
    print(photo_size.file_id)
    photo_info = {
        'url': photo_size.file_id,
    }
    
    photos.append(photo_info)
    await state.update_data(photos=photos)

    print(photos, flush=True)

    await message.answer(
        text="Добавьте три категории для вашего мероприятия. Вводите через запятую"
    )
    categories_text = get_compact_categories_text()

    await message.answer(
        text=categories_text,
        parse_mode="Markdown"
    )

    await state.set_state(EventCreation.categories)


def get_compact_categories_text() -> str:
    chunk_size = len(cats) // 3  # 3 столбца
    
    rows = []
    for i in range(0, len(cats), chunk_size):
        chunk = cats[i:i + chunk_size]
        row = "  ".join([f"• {cat}" for cat in chunk])
        rows.append(row)
    
    categories_text = "📂 *Доступные категории:*\n\n" + "\n".join(rows)
    return categories_text


@router.message(EventCreation.categories)
async def proccess_categories(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            text="Нужно неправильный формат категорий. Отправьте заново"
        )
        return
    
    cts = list(map(lambda x: x.strip(), message.text.split(',')))

    for c in cts:
        if c not in categories:
            await message.answer(
                text=f"Категории {c} нет в списке категорий"
            )
            return
        
    await state.update_data(categories=cts)

    await show_summary(message=message, state=state)

@router.message(EventCreation.confirmation)
async def show_summary(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos = data.get('photos', [])
    
    # Отправляем текстовую информацию
    preview_text = create_preview_text(data)
    
    if photos:
        if len(photos) == 1:
            # Отправка одного фото
            await message.answer_photo(
                photo=photos[0]['url'],
                caption="📷 *Добавленное фото:*",
                parse_mode="Markdown"
            )
        else:
            media_group = MediaGroupBuilder(caption="📷 *Добавленные фото:*")
            
            for photo_data in photos:
                media_group.add_photo(
                    media=photo_data['file_id']
                )
            
            # Отправляем медиагруппу
            await message.answer_media_group(
                media=media_group.build()
            )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_event"),
                types.InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_event")
            ],
            [
                types.InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_event")
            ]
        ]
    )
    # Отправляем пользователю сводку по мероприятию
    await message.answer(preview_text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "confirm_event")
async def handle_confirm_event(callback_query: types.CallbackQuery, state: FSMContext):
    # Отвечаем на callback
    await callback_query.answer()
    
    data = await state.get_data()
    print(data, flush=True)
    
    coords = data["coords"]
    print(coords, flush=True)
    print(data.get("photos", []), flush=True)
    category_ids = []

    for ct in data["categories"]:
        category_ids.append(categories[ct])

    event_data = {
        "name": data["name"],
        "description": data["description"],
        "date": str(data["date"].isoformat()),
        "address": data["location"],
        "longitude": coords[0],
        "latitude": coords[1],
        "age_restriction": int(data["age_restriction"]),
        "chat_link": "link",
        "max_participants": int(data["max_participants"]),
        "cost": 0,
        "balance": 0,
        "is_freezed": False,
        "photo_ids": data.get("photos", []),
        "organiser_id": callback_query.from_user.id,
        "category_ids": category_ids
    }

    print(event_data, flush=True)
    loading_msg = await callback_query.message.answer("📤 Отправляем данные...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://backend:8080/api/create_event',
                json=event_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200 or response.status == 201:
                    # Успех
                    result = await response.json()
                    
                    # Обновляем сообщение
                    await loading_msg.edit_text(
                        f"✅ Мероприятие создано!\n"
                        f"ID: {result.get('id')}\n"
                        f"Ссылка: {result.get('url', 'Нет')}"
                    )
                    
                    # Завершаем состояние FSM
                    await state.clear()
                    
                else:
                    # Ошибка
                    error = await response.text()
                    print(error)
                    await loading_msg.edit_text(f"❌ Ошибка: {response.status}\n{error[:200]}")
            
    except Exception as e:
        await loading_msg.edit_text(f"❌ Ошибка отправки: {str(e)}")

    await callback_query.message.edit_reply_markup(reply_markup=None)


async def cancel_creation(message: types.Message, state: FSMContext):
    await message.answer("Создание мероприятия отменено.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@router.message(Command('cancel'))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await cancel_creation(message, state)


def create_preview_text(data: dict) -> str:
    """Создает текстовый предпросмотр всех данных"""
    photos_count = len(data.get('photos', []))
    
    text = (
        "📋 *Предпросмотр мероприятия:*\n\n"
        f"*🏷 Название:* {data['name']}\n"
        f"*📝 Описание:* {data['description']}\n"
        f"*📅 Дата и время:* {data['date'].isoformat()}\n"
        f"*📍 Место:* {data['location']}\n"
        f"*👥 Макс. участников:* {data['max_participants']}\n"
        f"*🖼 Фото:* {photos_count} шт.\n"
        f"**Категории: {", ".join(data["categories"])}\n"
    )
    
    return text


@router.message(Command("edit_event"))
async def handle_edit_event(message: types.Message):
    await message.answer(
        text="Edit event"
    )


@router.message(Command("delete_event"))
async def handle_delete_event(message: types.Message):
    await message.answer(
        text="Delete event"
    )


@router.message(Command("created_events"))
async def handle_created_events(message: types.Message):
    await message.answer(
    text="Created event"
)