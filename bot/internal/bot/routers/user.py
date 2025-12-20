from __future__ import annotations

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import aiohttp

from internal.bot.categories import categories

router = Router(name=__name__)

# В docker-compose сети "localhost" НЕ указывает на backend-контейнер, поэтому используем "backend"
BACKEND_REGISTER_URL = "http://backend:8080/api/register"
BACKEND_ADD_CATEGORY_URL = "http://backend:8080/api/add_category"
BACKEND_RECOMMEND_URL = "http://backend:8080/api/get_recomend_post"
RECOMMENDER_CATEGORIES_URL = "http://recommender_system:8000/apiml/add_category/"

# Простейшее in-memory хранилище telegram_id -> user_id (Bearer token = user_id).
# Для продакшена лучше хранить в БД/Redis.
USER_ID_BY_TELEGRAM: dict[int, int] = {}

# Хранилище выбранных категорий пользователя (telegram_id -> список названий категорий)
USER_CATEGORIES: dict[int, list[str]] = {}


class UserRegister(StatesGroup):
    telegram_info_id = State()
    first_name = State()
    last_name = State()
    role = State()
    balance = State()
    coords = State()
    photo = State()
    confirmation = State()
    editing_field = State()


def _get_user_id_or_none(telegram_id: int) -> int | None:
    return USER_ID_BY_TELEGRAM.get(telegram_id)


def _main_menu_keyboard() -> types.InlineKeyboardMarkup:
    """Создает клавиатуру главного меню"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="👤 Регистрация", callback_data="menu_register"),
                types.InlineKeyboardButton(text="📂 Категории", callback_data="menu_categories"),
            ],
            [
                types.InlineKeyboardButton(text="🎯 Рекомендации", callback_data="menu_recommend"),
            ],
            [
                types.InlineKeyboardButton(text="➕ Создать мероприятие", callback_data="menu_create_event"),
                types.InlineKeyboardButton(text="📋 Мои мероприятия", callback_data="menu_created_events"),
            ],
            [
                types.InlineKeyboardButton(text="🔄 Обновить меню", callback_data="menu_refresh"),
            ],
        ]
    )


def _get_main_menu_text() -> str:
    """Формирует текст главного меню"""
    return (
        "🎉 *Добро пожаловать в Events Finder!*\n\n"
        "📌 *Доступные команды:*\n\n"
        "👤 *Для пользователей:*\n"
        "• `/register` - Регистрация в системе\n"
        "• `/categories` - Выбор категорий интересов\n"
        "• `/recommend` - Получить рекомендацию мероприятия\n\n"
        "🎭 *Для организаторов:*\n"
        "• `/create_event` - Создать новое мероприятие\n"
        "• `/created_events` - Просмотр созданных мероприятий\n"
        "• `/edit_event` - Редактировать мероприятие\n\n"
        "💡 *Используйте кнопки ниже для быстрого доступа к функциям*"
    )


# -------------------------
# START COMMAND (Главное меню)
# -------------------------

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start - показывает главное меню"""
    await state.clear()
    await message.answer(
        _get_main_menu_text(),
        parse_mode="Markdown",
        reply_markup=_main_menu_keyboard()
    )


@router.callback_query(F.data == "menu_register")
async def menu_register(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Регистрация' из главного меню"""
    await callback.answer()
    await state.clear()
    
    # Сразу сохраняем то, что можем взять из Telegram и значения по умолчанию
    await state.update_data(
        telegram={"telegram_id": callback.from_user.id},
        telegram_info={
            "id": 1,  # Автоматически устанавливаем 1
            "telegram_id": callback.from_user.id,
            "username": callback.from_user.username or "",
            "chat_id": callback.message.chat.id,
        },
        balance=23,  # Автоматически устанавливаем 23
        longitude=37.6173,  # Координаты Москвы по умолчанию
        latitude=55.7558,
        photo_id=None,  # Автоматически пропускаем фото
    )
    
    await callback.message.answer("Введите имя (first_name):")
    await state.set_state(UserRegister.first_name)


@router.callback_query(F.data == "menu_categories")
async def menu_categories(callback: types.CallbackQuery):
    """Обработчик кнопки 'Категории' из главного меню"""
    await callback.answer()
    user_id = _get_user_id_or_none(callback.from_user.id)
    if user_id is None:
        await callback.message.answer("Сначала зарегистрируйся командой /register, чтобы получить user_id.")
        return
    
    await callback.message.answer("Выбери категорию интересов:", reply_markup=_categories_keyboard())


@router.callback_query(F.data == "menu_recommend")
async def menu_recommend(callback: types.CallbackQuery):
    """Обработчик кнопки 'Рекомендации' из главного меню"""
    await callback.answer()
    user_id = _get_user_id_or_none(callback.from_user.id)
    if user_id is None:
        await callback.message.answer("Сначала зарегистрируйся (/register), чтобы получить user_id.")
        return
    
    await _send_recommendation(callback.message, user_id)


@router.callback_query(F.data == "menu_create_event")
async def menu_create_event(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Создать мероприятие' из главного меню"""
    await callback.answer()
    # Используем lazy import для избежания циклических импортов
    from .organiser import EventCreation
    await state.clear()
    await callback.message.answer(
        text="Введите название нового мероприятия"
    )
    await state.set_state(EventCreation.name)


@router.callback_query(F.data == "menu_created_events")
async def menu_created_events(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Мои мероприятия' из главного меню"""
    await callback.answer()
    try:
        # Отправляем запрос на получение мероприятий
        await state.update_data(telegram_id=callback.from_user.id)
        request_data = {
            "telegram_id": callback.from_user.id,
            "page": 1
        }
        
        loading_msg = await callback.message.answer("🔄 Загружаем ваши мероприятия...")
        
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
                    
                    # Используем lazy import для избежания циклических импортов
                    from .organiser import EventViewStates, show_events_page
                    
                    await state.set_state(EventViewStates.viewing_events)
                    await state.update_data({
                        'all_events': all_events,
                        'current_page': 0,
                        'total_pages': (total_cnt + 2) // 3,
                        'message_id': loading_msg.message_id
                    })
                    
                    # Показываем первую страницу
                    await show_events_page(
                        message=callback.message,
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
        await callback.message.answer("❌ Не удалось подключиться к серверу.")
    except Exception as e:
        await callback.message.answer(f"❌ Произошла ошибка: {str(e)}")


@router.callback_query(F.data == "menu_refresh")
async def menu_refresh(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Обновить меню' из главного меню"""
    await callback.answer("🔄 Меню обновлено")
    await callback.message.edit_text(
        _get_main_menu_text(),
        parse_mode="Markdown",
        reply_markup=_main_menu_keyboard()
    )


def _role_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="PARTICIPANT", callback_data="reg_role:PARTICIPANT"),
                types.InlineKeyboardButton(text="ORGANISER", callback_data="reg_role:ORGANISER"),
            ],
            [types.InlineKeyboardButton(text="Отмена", callback_data="reg_cancel")],
        ]
    )


def _confirm_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Подтвердить", callback_data="reg_confirm"),
                types.InlineKeyboardButton(text="✏️ Изменить", callback_data="reg_edit"),
            ],
            [types.InlineKeyboardButton(text="❌ Отменить", callback_data="reg_cancel")],
        ]
    )


def _edit_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Имя", callback_data="reg_edit_field:first_name"),
                types.InlineKeyboardButton(text="Фамилия", callback_data="reg_edit_field:last_name"),
            ],
            [
                types.InlineKeyboardButton(text="Роль", callback_data="reg_edit_field:role"),
            ],
            [types.InlineKeyboardButton(text="Назад", callback_data="reg_back_to_summary")],
        ]
    )


def _make_preview_text(data: dict) -> str:
    tg = data.get("telegram", {})
    ti = data.get("telegram_info", {})
    photo_id = data.get("photo_id")
    longitude = data.get("longitude")
    latitude = data.get("latitude")

    return (
        "📋 *Предпросмотр регистрации*\n\n"
        f"*telegram_id (root):* {tg.get('telegram_id')}\n"
        f"*telegram_info.id:* {ti.get('id')}\n"
        f"*telegram_info.telegram_id:* {ti.get('telegram_id')}\n"
        f"*telegram_info.username:* {ti.get('username')}\n"
        f"*telegram_info.chat_id:* {ti.get('chat_id')}\n\n"
        f"*first_name:* {data.get('first_name')}\n"
        f"*last_name:* {data.get('last_name')}\n"
        f"*role:* {data.get('role')}\n"
        f"*balance:* {data.get('balance')}\n"
        f"*longitude:* {longitude}\n"
        f"*latitude:* {latitude}\n"
        f"*photo_id:* {photo_id}\n"
    )


async def _show_summary(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    text = _make_preview_text(data)
    await state.set_state(UserRegister.confirmation)
    await message.answer(text, parse_mode="Markdown", reply_markup=_confirm_keyboard())


# -------------------------
# REGISTER FLOW
# -------------------------

@router.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    await state.clear()

    # Сразу сохраняем то, что можем взять из Telegram и значения по умолчанию
    await state.update_data(
        telegram={"telegram_id": message.from_user.id},
        telegram_info={
            "id": 1,  # Автоматически устанавливаем 1
            "telegram_id": message.from_user.id,
            "username": message.from_user.username or "",
            "chat_id": message.chat.id,
        },
        balance=23,  # Автоматически устанавливаем 23
        longitude=37.6173,  # Координаты Москвы по умолчанию
        latitude=55.7558,
        photo_id=None,  # Автоматически пропускаем фото
    )

    await message.answer("Введите имя (first_name):")
    await state.set_state(UserRegister.first_name)


@router.message(UserRegister.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Нужно текстом. Введите имя ещё раз:")
        return

    await state.update_data(first_name=message.text)

    data = await state.get_data()
    if data.get("editing_field"):
        await state.update_data(editing_field=False)
        await _show_summary(message, state)
        return

    await message.answer("Введите фамилию (last_name):")
    await state.set_state(UserRegister.last_name)


@router.message(UserRegister.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Нужно текстом. Введите фамилию ещё раз:")
        return

    await state.update_data(last_name=message.text)

    data = await state.get_data()
    if data.get("editing_field"):
        await state.update_data(editing_field=False)
        await _show_summary(message, state)
        return

    await message.answer("Выберите роль:", reply_markup=_role_keyboard())
    await state.set_state(UserRegister.role)


@router.callback_query(F.data.startswith("reg_role:"))
async def process_role_cb(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    role = callback.data.split(":", 1)[1]

    await state.update_data(role=role)

    data = await state.get_data()
    if data.get("editing_field"):
        await state.update_data(editing_field=False)
        await _show_summary(callback.message, state)
        return

    # После выбора роли сразу показываем summary (все остальные поля уже заполнены автоматически)
    await _show_summary(callback.message, state)








@router.callback_query(F.data == "reg_edit")
async def reg_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Что изменить?", reply_markup=_edit_keyboard())


@router.callback_query(F.data.startswith("reg_edit_field:"))
async def reg_edit_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    field = callback.data.split(":", 1)[1]
    await state.update_data(editing_field=True)

    if field == "first_name":
        await callback.message.answer("Введите имя (first_name):")
        await state.set_state(UserRegister.first_name)
    elif field == "last_name":
        await callback.message.answer("Введите фамилию (last_name):")
        await state.set_state(UserRegister.last_name)
    elif field == "role":
        await callback.message.answer("Выберите роль:", reply_markup=_role_keyboard())
        await state.set_state(UserRegister.role)
    else:
        await callback.message.answer("Неизвестное поле.")


@router.callback_query(F.data == "reg_back_to_summary")
async def reg_back_to_summary(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await _show_summary(callback.message, state)


@router.callback_query(F.data == "reg_cancel")
async def reg_cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Отменено")
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data == "reg_confirm")
async def reg_confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    payload = {
        "telegram_id": 2,
        "user": {
            "telegram_info": {
                "id": data["telegram_info"]["id"],  # Используем сохраненное значение (1)
                "telegram_id": data["telegram_info"]["telegram_id"],
                "username": data["telegram_info"]["username"],
                "chat_id": data["telegram_info"]["chat_id"],
            },
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "role": data["role"],
            "balance": data["balance"],  # Используем сохраненное значение (23)
            "longitude": float(data["longitude"]),  # Используем сохраненное значение
            "latitude": float(data["latitude"]),  # Используем сохраненное значение
            "photo_id": data.get("photo_id"),  # None по умолчанию
        },
    }

    loading = await callback.message.answer("📤 Регистрируем пользователя...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BACKEND_REGISTER_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                if resp.status in (200, 201):
                    result = await resp.json()

                    # Пытаемся сохранить user_id как Bearer token
                    user_id = result.get("user")
                    if isinstance(user_id, int):
                        USER_ID_BY_TELEGRAM[callback.from_user.id] = user_id
                        # Инициализируем список категорий для нового пользователя
                        USER_CATEGORIES[callback.from_user.id] = []

                    await loading.edit_text(f"✅ Успех. Ответ сервера: {result}")
                    await state.clear()
                else:
                    text = await resp.text()
                    await loading.edit_text(f"❌ Ошибка {resp.status}: {text[:500]}")
    except Exception as e:
        await loading.edit_text(f"❌ Ошибка отправки: {e}")


# -------------------------
# CATEGORIES (add_category)
# -------------------------

def _categories_keyboard() -> types.InlineKeyboardMarkup:
    rows: list[list[types.InlineKeyboardButton]] = []
    # categories - это словарь {название: id}
    for cat_name, cat_id in categories.items():
        rows.append([
            types.InlineKeyboardButton(
                text=cat_name,
                callback_data=f"cat_pick:{cat_id}",
            )
        ])
    rows.append([types.InlineKeyboardButton(text="Отмена", callback_data="cat_cancel")])
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("categories"))
async def cmd_categories(message: types.Message):
    user_id = _get_user_id_or_none(message.from_user.id)
    if user_id is None:
        await message.answer("Сначала зарегистрируйся командой /register, чтобы получить user_id.")
        return

    await message.answer("Выбери категорию интересов:", reply_markup=_categories_keyboard())


@router.callback_query(F.data == "cat_cancel")
async def cat_cancel(callback: types.CallbackQuery):
    await callback.answer("Отменено")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("cat_pick:"))
async def cat_pick(callback: types.CallbackQuery):
    await callback.answer()
    user_id = _get_user_id_or_none(callback.from_user.id)
    if user_id is None:
        await callback.message.answer("Не найден user_id. Пройди /register ещё раз.")
        return

    cat_id = int(callback.data.split(":", 1)[1])
    
    # Находим название категории по ID
    cat_name = None
    for name, cid in categories.items():
        if cid == cat_id:
            cat_name = name
            break
    
    if cat_name is None:
        await callback.message.answer(f"❌ Категория с id={cat_id} не найдена.")
        return

    payload = {"id_cat": cat_id}
    headers = {
        "Authorization": f"Bearer {user_id}",
        "Content-Type": "application/json",
    }

    msg = await callback.message.answer("📌 Сохраняю категорию...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(BACKEND_ADD_CATEGORY_URL, json=payload, headers=headers) as resp:
                if resp.status in (200, 201):
                    data = await resp.json()
                    
                    # Сохраняем категорию в список выбранных
                    telegram_id = callback.from_user.id
                    if telegram_id not in USER_CATEGORIES:
                        USER_CATEGORIES[telegram_id] = []
                    if cat_name not in USER_CATEGORIES[telegram_id]:
                        USER_CATEGORIES[telegram_id].append(cat_name)
                    
                    await msg.edit_text(f"✅ Категория '{cat_name}' сохранена!")
                    
                    # Получаем рекомендации на основе выбранных категорий
                    await _show_category_recommendations(callback.message, telegram_id)
                else:
                    text = await resp.text()
                    await msg.edit_text(f"❌ Ошибка {resp.status}: {text[:500]}")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка отправки: {e}")


async def _get_category_recommendations(user_categories: list[str], top_k: int = 5) -> list[str]:
    """Получает рекомендации категорий от recommender system"""
    if not user_categories:
        return []
    
    payload = {
        "categories": user_categories,
        "top_k": top_k
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                RECOMMENDER_CATEGORIES_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("recommendations", [])
                else:
                    return []
    except Exception as e:
        print(f"Ошибка получения рекомендаций: {e}")
        return []


def _recommended_categories_keyboard(recommended_cats: list[str], user_categories: list[str]) -> types.InlineKeyboardMarkup:
    """Создает клавиатуру с рекомендованными категориями"""
    rows: list[list[types.InlineKeyboardButton]] = []
    
    # Фильтруем рекомендации - убираем уже выбранные категории
    available_recommendations = [cat for cat in recommended_cats if cat not in user_categories]
    
    # Показываем только первые 5 доступных рекомендаций
    for cat_name in available_recommendations[:5]:
        cat_id = categories.get(cat_name)
        if cat_id:
            rows.append([
                types.InlineKeyboardButton(
                    text=f"➕ {cat_name}",
                    callback_data=f"cat_pick:{cat_id}"
                )
            ])
    
    if not rows:
        # Если нет доступных рекомендаций, показываем кнопку "Закрыть"
        rows.append([types.InlineKeyboardButton(text="✅ Все рекомендации добавлены", callback_data="rec_cats_close")])
    else:
        rows.append([types.InlineKeyboardButton(text="❌ Закрыть", callback_data="rec_cats_close")])
    
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_category_recommendations(message: types.Message, telegram_id: int):
    """Показывает рекомендованные категории пользователю"""
    user_cats = USER_CATEGORIES.get(telegram_id, [])
    
    if not user_cats:
        return
    
    loading_msg = await message.answer("🔍 Ищу подходящие категории...")
    
    recommended = await _get_category_recommendations(user_cats, top_k=5)
    
    if not recommended:
        await loading_msg.edit_text(
            "✅ Категория добавлена!\n\n"
            "К сожалению, рекомендации пока недоступны."
        )
        return
    
    # Фильтруем уже выбранные категории
    available_recs = [cat for cat in recommended if cat not in user_cats]
    
    if not available_recs:
        await loading_msg.edit_text(
            "✅ Категория добавлена!\n\n"
            "🎉 Вы уже добавили все рекомендованные категории!"
        )
        return
    
    text = (
        "✅ Категория добавлена!\n\n"
        "💡 *Рекомендуемые категории:*\n\n"
    )
    
    for i, cat_name in enumerate(available_recs[:5], 1):
        text += f"{i}. {cat_name}\n"
    
    text += "\n_Выберите категории для добавления:_"
    
    await loading_msg.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=_recommended_categories_keyboard(recommended, user_cats)
    )


@router.callback_query(F.data == "rec_cats_close")
async def rec_cats_close(callback: types.CallbackQuery):
    """Закрывает сообщение с рекомендациями"""
    await callback.answer()
    await callback.message.delete()


# -------------------------
# RECOMMEND EVENT
# -------------------------

def _event_text(event: dict) -> str:
    return (
        "🎯 *Рекомендуемое мероприятие*\n\n"
        f"*Название:* {event.get('name')}\n"
        f"*Описание:* {event.get('description')}\n"
        f"*Дата:* {event.get('date')}\n"
        f"*Адрес:* {event.get('address')}\n"
        f"*Возраст:* {event.get('age_restriction')}\n"
        f"*Стоимость:* {event.get('cost')}\n"
        f"*Баланс события:* {event.get('balance')}\n"
        f"*Чат:* {event.get('chat_link')}\n"
    )


def _event_keyboard(event: dict) -> types.InlineKeyboardMarkup:
    rows: list[list[types.InlineKeyboardButton]] = []
    chat_link = event.get("chat_link")
    if isinstance(chat_link, str) and chat_link:
        rows.append([types.InlineKeyboardButton(text="Открыть чат", url=chat_link)])
    rows.append([types.InlineKeyboardButton(text="Ещё рекомендация", callback_data="rec_again")])
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_recommendation(target_message: types.Message, user_id: int):
    headers = {"Authorization": f"Bearer {user_id}"}

    loading = await target_message.answer("🔎 Ищу рекомендацию...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BACKEND_RECOMMEND_URL, headers=headers) as resp:
                if resp.status == 200:
                    event = await resp.json()
                    await loading.edit_text(
                        _event_text(event),
                        parse_mode="Markdown",
                        reply_markup=_event_keyboard(event),
                    )
                elif resp.status == 404:
                    text = await resp.text()
                    await loading.edit_text(
                        "Пока нет рекомендаций: добавь категории через /categories.\n"
                        f"Ответ сервера: {text[:300]}"
                    )
                else:
                    text = await resp.text()
                    await loading.edit_text(f"❌ Ошибка {resp.status}: {text[:500]}")
    except Exception as e:
        await loading.edit_text(f"❌ Ошибка запроса: {e}")


@router.message(Command("recommend"))
async def cmd_recommend(message: types.Message):
    user_id = _get_user_id_or_none(message.from_user.id)
    if user_id is None:
        await message.answer("Сначала зарегистрируйся (/register), чтобы получить user_id.")
        return

    await _send_recommendation(message, user_id)


@router.callback_query(F.data == "rec_again")
async def rec_again(callback: types.CallbackQuery):
    await callback.answer()
    user_id = _get_user_id_or_none(callback.from_user.id)
    if user_id is None:
        await callback.message.answer("Не найден user_id. Пройди /register ещё раз.")
        return

    await _send_recommendation(callback.message, user_id)
