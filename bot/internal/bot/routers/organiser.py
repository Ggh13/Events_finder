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
    editing_field = State()


@router.message(Command("create_event"))
async def handle_create_event(message: types.Message, state: FSMContext):
    await state.clear()
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
        # await state.set_state(EventCreation.confirmation)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
        await message.answer(
            text="Введите дату и время мероприятия в формате 2021-02-01T15:30"
        )
        await state.set_state(EventCreation.date)


@router.message(EventCreation.date)
async def proccess_date(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Неправильный формат даты. Введите заново"
        )
        return
    
    try:
        date = datetime.fromisoformat(message.text)
    except ValueError as e:
        await message.answer(
            "Неправильный формат даты. Введите заново"
        )
        return
    await state.update_data(date=date)

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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
    
    await state.update_data(coords=coords)

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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

    data = await state.get_data()
    is_editing = data.get("editing_field", False)
    if is_editing:
        await state.update_data(editing_field=False)
        await show_summary(message=message, state=state)
    else:
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
                f'http://backend:8080/api/create_event',
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


@router.callback_query(F.data == "cancel_event")
async def cmd_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Создание мероприятия отменено.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await callback_query.message.edit_reply_markup(reply_markup=None)


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


class EventViewStates(StatesGroup):
    """Состояния для просмотра мероприятий"""
    viewing_events = State()


@router.message(Command("created_events"))
async def handle_created_events(message: types.Message, state: FSMContext):
    """Обработчик команды просмотра созданных мероприятий"""
    try:
        # Отправляем запрос на получение мероприятий
        await state.update_data(telegram_id=message.from_user.id)
        request_data = {
            "telegram_id": message.from_user.id,
            "page": 1  # Получаем все события, так как будем пагинировать на стороне бота
        }
        
        loading_msg = await message.answer("🔄 Загружаем ваши мероприятия...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'http://backend:8080/api/get_events',
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    resp = await response.json()
                    all_events = resp.get("events", [])
                    total_cnt = resp.get("total_cnt", 0)

                    await state.update_data(total_cnt=total_cnt)
                    
                    if not all_events:
                        await loading_msg.edit_text("📭 У вас пока нет созданных мероприятий.")
                        return
                    
                    # Сохраняем все события в состояние с пагинацией
                    await state.set_state(EventViewStates.viewing_events)
                    await state.update_data({
                        'all_events': all_events,
                        'current_page': 0,  # Номер текущей страницы (начинаем с 0)
                        'total_pages': (total_cnt + 2) // 3,  # Округляем вверх
                        'message_id': loading_msg.message_id  # ID сообщения для редактирования
                    })
                    
                    # Показываем первую страницу
                    await show_events_page(
                        message=message,
                        state=state,
                        all_events=all_events,
                        page=0,
                        total_pages=(total_cnt + 2) // 3,
                        edit_message_id=loading_msg.message_id
                    )
                    
                elif response.status == 404:
                    await loading_msg.edit_text("📭 Мероприятий не найдено.")
                else:
                    error = await response.text()
                    await loading_msg.edit_text(f"❌ Ошибка загрузки мероприятий: {response.status}")
                    
    except aiohttp.ClientConnectorError:
        await loading_msg.edit_text("❌ Не удалось подключиться к серверу.")
    except Exception as e:
        await loading_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")


async def show_events_page(
    message: types.Message, 
    state: FSMContext, 
    all_events: list, 
    page: int, 
    total_pages: int,
    edit_message_id: int = None
):
    """Отображает страницу с 3 мероприятиями"""
    telegram_id = await state.get_value("telegram_id")
    request_data = {
        "telegram_id": telegram_id,
        "page": page + 1  # Получаем все события, так как будем пагинировать на стороне бота
    }

    print("Current page:", page, flush=True)
    current_events = []
    async with aiohttp.ClientSession() as session:
            async with session.get(
                'http://backend:8080/api/get_events',
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    resp = await response.json()
                    print(resp, flush=True)
                    current_events = resp.get("events", [])
                    
                elif response.status == 404:
                    await message.answer("📭 Мероприятий не найдено.")
                else:
                    error = await response.text()
                    await message.answer(f"❌ Ошибка загрузки мероприятий: {response.status}")
    
    if not current_events:
        await message.answer("❌ Ошибка: нет событий для отображения")
        return
    
    # Создаем клавиатуру с кнопками событий
    keyboard_buttons = []
    
    for event in current_events:
        event_id = event.get('id', '')
        event_name = event.get('name', 'Без названия')
        # Обрезаем слишком длинные названия
        display_name = event_name[:30] + "..." if len(event_name) > 30 else event_name
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"📋 {display_name}",
                callback_data=f"view_event_detail:{event_id}:{page}"
            )
        ])
    
    # Добавляем кнопки навигации
    navigation_buttons = []
    
    if page > 0:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="◀️ Назад", callback_data=f"events_prev:{page}")
        )
    
    navigation_buttons.append(
        types.InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="noop")
    )
    
    if page < total_pages - 1:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="Вперед ▶️", callback_data=f"events_next:{page}")
        )
    
    if navigation_buttons:
        keyboard_buttons.append(navigation_buttons)
    
    # # Кнопка для возврата к списку (если мы в деталях)
    # keyboard_buttons.append([
    #     types.InlineKeyboardButton(text="🔄 Обновить список", callback_data="refresh_events")
    # ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Текст сообщения
    message_text = f"📋 *Ваши мероприятия (стр. {page + 1}/{total_pages}):*\n\n"
    
    for i, event in enumerate(current_events, start=1):
        event_name = event.get('name', 'Без названия')
        # Обрезаем описание для предпросмотра
        description = event.get('description', '')
        short_description = description[:50] + "..." if len(description) > 50 else description
        
        message_text += f"{i}. *{event_name}*\n"
        message_text += f"   {short_description}\n\n"
    
    # Отправляем или редактируем сообщение
    if edit_message_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=edit_message_id,
                text=message_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            # Если не удалось редактировать, отправляем новое
            print("# Если не удалось редактировать, отправляем новое", flush=True)
            await message.answer(message_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer(message_text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data.startswith("events_"))
async def handle_events_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик навигации по страницам мероприятий"""
    await callback_query.answer()
    
    data = await state.get_data()
    all_events = data.get('all_events', [])
    total_cnt = data.get('total_cnt', 0)
    current_page = data.get('current_page', 0)
    
    if callback_query.data.startswith("events_next:"):
        # Переход на следующую страницу
        try:
            page = int(callback_query.data.split(":")[1])
            if page < (total_cnt + 2) // 3 - 1:
                page += 1
            else:
                await callback_query.answer("Это последняя страница")
                return
        except (ValueError, IndexError):
            page = current_page + 1
    
    elif callback_query.data.startswith("events_prev:"):
        # Переход на предыдущую страницу
        try:
            page = int(callback_query.data.split(":")[1])
            if page > 0:
                page -= 1
            else:
                await callback_query.answer("Это первая страница")
                return
        except (ValueError, IndexError):
            page = max(current_page - 1, 0)
    
    
    # Обновляем состояние
    await state.update_data(current_page=page)
    
    # Показываем новую страницу
    total_pages = (total_cnt + 2) // 3
    await show_events_page(
        message=callback_query.message,
        state=state,
        all_events=all_events,
        page=page,
        total_pages=total_pages,
        edit_message_id=callback_query.message.message_id
    )


@router.callback_query(F.data.startswith("view_event_detail:"))
async def handle_view_event_detail(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик просмотра деталей мероприятия"""
    await callback_query.answer()
    
    try:
        # Парсим callback_data: view_event_detail:event_id:page
        parts = callback_query.data.split(":")
        if len(parts) < 3:
            await callback_query.message.answer("❌ Ошибка формата данных")
            return
        
        event_id = parts[1]
        page = int(parts[2])
        
        # Сохраняем текущую страницу в состоянии
        await state.update_data(current_page=page)
        
        # Запрашиваем детали мероприятия
        event_details = await get_event_details(event_id=event_id, telegram_id=callback_query.from_user.id)
        
        if not event_details:
            await callback_query.message.answer("❌ Не удалось загрузить информацию о мероприятии.")
            return
        
        # Формируем сообщение с деталями
        details_text = format_event_details(event_details)
        
        # Получаем фото мероприятия
        photos = event_details.get('photo_ids', [])
        photo_url = photos[0].get('url') if photos else None
        
        # Клавиатура для детального просмотра
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="◀️ Назад к списку", callback_data=f"back_to_list:{page}"),
                    types.InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_event:{event_id}")
                ],
                [
                    types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_event:{event_id}"),
                    types.InlineKeyboardButton(text="👥 Участники", callback_data=f"event_participants:{event_id}")
                ]
            ]
        )
        
        # Отправляем фото с подписью или просто текст
        if photo_url:
            media = types.InputMediaPhoto(media=photo_url, caption=details_text, parse_mode="Markdown")
            await callback_query.message.edit_media(
                media=media,
                reply_markup=keyboard
            )
        else:
            await callback_query.message.edit_text(
                details_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
    except Exception as e:
        await callback_query.message.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("back_to_list:"))
async def handle_back_to_list(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик возврата к списку мероприятий"""
    await callback_query.answer()
    
    try:
        print(callback_query.data.split(":"), flush=True)
        page = int(callback_query.data.split(":")[1])
        data = await state.get_data()
        all_events = data["all_events"]

        print("ALL EVENTS BACK TO LIST", all_events, flush=True)
        
        # Удаляем сообщение с деталями
        await callback_query.message.delete()
        print("DELETED", flush=True)
        total_cnt = data.get("total_cnt", 0)
        # Показываем список мероприятий на указанной странице
        total_pages = (total_cnt + 2) // 3
        await show_events_page(
            message=callback_query.message,
            state=state,
            all_events=all_events,
            page=page,
            total_pages=total_pages,
            edit_message_id=None  # Отправляем новое сообщение
        )
        
    except Exception as e:
        await callback_query.message.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(F.data == "refresh_events")
async def handle_refresh_events(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик обновления списка мероприятий"""
    await callback_query.answer("🔄 Обновляем...")
    
    # Получаем данные пользователя из состояния
    data = await state.get_data()
    user_id = callback_query.from_user.id
    
    try:
        # Запрашиваем обновленный список мероприятий
        request_data = {
            "telegram_id": user_id,
            "page": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'http://backend:8080/api/get_events',
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    all_events = result.get('events', [])
                    
                    if not all_events:
                        await callback_query.message.edit_text("📭 У вас пока нет созданных мероприятий.")
                        return
                    
                    # Обновляем состояние
                    await state.update_data({
                        'all_events': all_events,
                        'current_page': 0,
                        'total_pages': (len(all_events) + 2) // 3
                    })
                    
                    # Показываем первую страницу
                    total_pages = (len(all_events) + 2) // 3
                    await show_events_page(
                        message=callback_query.message,
                        state=state,
                        all_events=all_events,
                        page=0,
                        total_pages=total_pages,
                        edit_message_id=callback_query.message.message_id
                    )
                else:
                    await callback_query.message.edit_text("❌ Не удалось обновить список мероприятий.")
                    
    except Exception as e:
        await callback_query.message.edit_text(f"❌ Ошибка обновления: {str(e)}")


async def get_event_details(event_id: int, telegram_id: int) -> dict:
    """Получает детальную информацию о мероприятии"""
    params = {
        "event_id": event_id,
        "telegram_id": telegram_id
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f'http://backend:8080/api/get_event/',
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
    except Exception:
        return None


def format_event_details(event: dict) -> str:
    """Форматирует детальную информацию о мероприятии"""
    # Форматируем дату
    date_str = "Не указана"
    event_date = event.get('date')
    if event_date:
        try:
            if isinstance(event_date, str):
                if 'T' in event_date:
                    dt = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(event_date)
                date_str = dt.strftime("%d.%m.%Y %H:%M")
            elif isinstance(event_date, datetime):
                date_str = event_date.strftime("%d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            date_str = str(event_date)
    
    # Форматируем координаты
    coords_str = ""
    longitude = event.get('longitude')
    latitude = event.get('latitude')
    if longitude and latitude:
        coords_str = f"{latitude}, {longitude}"
    
    details = [
        f"📋 *Детали мероприятия*\n",
        f"*🏷 Название:* {event.get('name', 'Не указано')}",
        f"*📝 Описание:* {event.get('description', 'Не указано')}",
        f"*📅 Дата и время:* {date_str}",
        f"*📍 Место проведения:* {event.get('address', 'Не указано')}",
        f"*🗺 Координаты:* {coords_str}" if coords_str else "",
        f"*👥 Макс. участников:* {event.get('max_participants', 'Не ограничено')}",
        f"*🎂 Ограничение по возрасту:* {event.get('age_restriction', 'Нет')}+",
        f"*🔗 Ссылка на чат:* {event.get('chat_link', 'Не указана')}",
        f"*💰 Цена:* {event.get('cost', 0)} руб.",
        f"*📂 Категории:* {', '.join(event.get('categories', []))}",
        f"*👤 Организатор:* {event.get('organiser_id', '')}",
        f"*🖼 Фото:* {len(event.get('photo_ids', []))} шт.",
        f"*🆔 ID:* `{event.get('id', 'Нет')}`"
    ]
    
    # Убираем пустые строки
    details = [d for d in details if d]
    return "\n".join(details)


# Обработчики для других действий с мероприятиями
@router.callback_query(F.data.startswith("edit_event:"))
async def handle_edit_existing_event(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик редактирования существующего мероприятия"""
    await callback_query.answer("✏️ Редактирование мероприятия")
    # Здесь можно реализовать логику редактирования
    event_id = callback_query.data.split(":")[1]
    await callback_query.message.answer(f"Редактирование мероприятия {event_id} будет реализовано позже.")


@router.callback_query(F.data.startswith("delete_event:"))
async def handle_delete_event(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик удаления мероприятия"""
    await callback_query.answer("🗑 Удаление мероприятия")
    # Здесь можно реализовать логику удаления
    event_id = callback_query.data.split(":")[1]
    await callback_query.message.answer(f"Удаление мероприятия {event_id} будет реализовано позже.")


@router.callback_query(F.data.startswith("event_participants:"))
async def handle_event_participants(callback_query: types.CallbackQuery):
    """Обработчик просмотра участников мероприятия"""
    await callback_query.answer("👥 Участники мероприятия")
    # Здесь можно реализовать логику просмотра участников
    event_id = callback_query.data.split(":")[1]
    await callback_query.message.answer(f"Просмотр участников мероприятия {event_id} будет реализовано позже.")

async def send_long_message(message: types.Message, text: str, max_length: int = 4000):
    """Отправляет длинное сообщение частями"""
    for i in range(0, len(text), max_length):
        part = text[i:i + max_length]
        if i == 0:
            await message.answer(part, parse_mode="Markdown")
        else:
            await message.answer(part, parse_mode="Markdown")
    

@router.callback_query(F.data == "edit_event")
async def handle_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    # Клавиатура для выбора поля для редактирования
    edit_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Название", callback_data="edit_field:name"),
                types.InlineKeyboardButton(text="Описание", callback_data="edit_field:description")
            ],
            [
                types.InlineKeyboardButton(text="Дата и время", callback_data="edit_field:date"),
                types.InlineKeyboardButton(text="Место", callback_data="edit_field:location")
            ],
            [
                types.InlineKeyboardButton(text="Координаты", callback_data="edit_field:coords"),
                types.InlineKeyboardButton(text="Ссылка на чат", callback_data="edit_field:chat_link")
            ],
            [
                types.InlineKeyboardButton(text="Макс. участников", callback_data="edit_field:max_participants"),
                types.InlineKeyboardButton(text="Возраст", callback_data="edit_field:age_restriction")
            ],
            [
                types.InlineKeyboardButton(text="Фото", callback_data="edit_field:photos"),
                types.InlineKeyboardButton(text="Категории", callback_data="edit_field:categories")
            ],
            [
                types.InlineKeyboardButton(text="◀️ Назад к просмотру", callback_data="back_to_summary")
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Выберите поле, которое хотите изменить:",
        reply_markup=edit_keyboard
    )


@router.callback_query(F.data.startswith("edit_field:"))
async def handle_edit_field(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    field = callback_query.data.split(":")[1]
    data = await state.get_data()
    
    # Устанавливаем состояние редактирования и переходим к соответствующему состоянию
    await state.update_data(editing_field=True)
    
    # Запрашиваем новое значение для выбранного поля
    if field == "name":
        await callback_query.message.edit_text(
            text="Введите новое название мероприятия:"
        )
        await state.set_state(EventCreation.name)
    
    elif field == "description":
        await callback_query.message.edit_text(
            text="Введите новое описание мероприятия:"
        )
        await state.set_state(EventCreation.description)
    
    elif field == "date":
        await callback_query.message.edit_text(
            text="Введите новую дату и время мероприятия в формате 2021-02-01T15:30:"
        )
        await state.set_state(EventCreation.date)
    
    elif field == "location":
        await callback_query.message.edit_text(
            text="Введите новый адрес мероприятия:"
        )
        await state.set_state(EventCreation.location)
    
    elif field == "coords":
        await callback_query.message.edit_text(
            text="Введите новые координаты (формат: 55.7558, 37.6173):"
        )
        await state.set_state(EventCreation.coords)
    
    elif field == "chat_link":
        await callback_query.message.edit_text(
            text="Введите новую ссылку на чат:"
        )
        await state.set_state(EventCreation.chat_link)
    
    elif field == "max_participants":
        await callback_query.message.edit_text(
            text="Введите новое максимальное количество участников:"
        )
        await state.set_state(EventCreation.max_participants)
    
    elif field == "age_restriction":
        await callback_query.message.edit_text(
            text="Введите новое ограничение по возрасту:"
        )
        await state.set_state(EventCreation.age_restriction)
    
    elif field == "photos":
        await callback_query.message.edit_text(
            text="Отправьте новое фото для мероприятия:"
        )
        await state.set_state(EventCreation.photos)
    
    elif field == "categories":
        categories_text = get_compact_categories_text()
        await callback_query.message.edit_text(
            text=f"Введите новые категории (через запятую):\n\n{categories_text}",
            parse_mode="Markdown"
        )
        await state.set_state(EventCreation.categories)

