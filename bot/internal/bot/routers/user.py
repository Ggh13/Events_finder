from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import aiohttp

router = Router(name=__name__)

BACKEND_REGISTER_URL = "http://localhost/api/register"  # поменяй на свой URL


class UserRegister(StatesGroup):
    telegram_info_id = State()   # это поле "telegram_info.id" из твоего примера
    first_name = State()
    last_name = State()
    role = State()
    balance = State()
    coords = State()             # "longitude, latitude" текстом или локацией
    photo = State()              # опционально
    confirmation = State()
    editing_field = State()


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
                types.InlineKeyboardButton(text="Баланс", callback_data="reg_edit_field:balance"),
            ],
            [
                types.InlineKeyboardButton(text="Координаты", callback_data="reg_edit_field:coords"),
                types.InlineKeyboardButton(text="Фото", callback_data="reg_edit_field:photo"),
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


@router.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    await state.clear()

    # Сразу сохраняем то, что можем взять из Telegram
    await state.update_data(
        telegram={"telegram_id": message.from_user.id},
        telegram_info={
            # id попросим у пользователя отдельным шагом, т.к. это твой внутренний id
            "id": None,
            "telegram_id": message.from_user.id,
            "username": message.from_user.username or "",
            "chat_id": message.chat.id,
        },
        photo_id=None,
    )

    await message.answer("Введите telegram_info.id (внутренний id в БД, число):")
    await state.set_state(UserRegister.telegram_info_id)


@router.message(UserRegister.telegram_info_id)
async def process_telegram_info_id(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Нужно число. Введите telegram_info.id ещё раз:")
        return
    try:
        tid = int(message.text)
    except ValueError:
        await message.answer("Нужно число. Введите telegram_info.id ещё раз:")
        return

    data = await state.get_data()
    ti = data["telegram_info"]
    ti["id"] = tid
    await state.update_data(telegram_info=ti)

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

    await callback.message.answer("Введите balance (целое число, например 0):")
    await state.set_state(UserRegister.balance)


@router.message(UserRegister.balance)
async def process_balance(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Нужно число. Введите balance ещё раз:")
        return
    try:
        balance = int(message.text)
    except ValueError:
        await message.answer("Нужно число. Введите balance ещё раз:")
        return

    await state.update_data(balance=balance)

    data = await state.get_data()
    if data.get("editing_field"):
        await state.update_data(editing_field=False)
        await _show_summary(message, state)
        return

    await message.answer(
        "Введите координаты в формате `longitude, latitude` (например `37.6, 55.7`) "
        "или отправьте локацию Telegram:",
        parse_mode="Markdown",
    )
    await state.set_state(UserRegister.coords)


@router.message(UserRegister.coords)
async def process_coords(message: types.Message, state: FSMContext):
    # вариант 1: Telegram location
    if message.location:
        # В Telegram location: latitude/longitude
        await state.update_data(
            latitude=float(message.location.latitude),
            longitude=float(message.location.longitude),
        )
        data = await state.get_data()
        if data.get("editing_field"):
            await state.update_data(editing_field=False)
            await _show_summary(message, state)
            return

        await message.answer("Отправьте фото (или напишите `skip`, чтобы photo_id = null):")
        await state.set_state(UserRegister.photo)
        return

    # вариант 2: текстом
    if not message.text:
        await message.answer("Нужно либо локацию, либо текст `longitude, latitude`. Повторите:")
        return

    try:
        parts = [p.strip() for p in message.text.split(",")]
        if len(parts) != 2:
            raise ValueError("bad format")
        longitude = float(parts[0])
        latitude = float(parts[1])
    except Exception:
        await message.answer("Неправильный формат. Пример: `37.6, 55.7`")
        return

    await state.update_data(longitude=longitude, latitude=latitude)

    data = await state.get_data()
    if data.get("editing_field"):
        await state.update_data(editing_field=False)
        await _show_summary(message, state)
        return

    await message.answer("Отправьте фото (или напишите `skip`, чтобы photo_id = null):")
    await state.set_state(UserRegister.photo)


@router.message(UserRegister.photo)
async def process_photo(message: types.Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "skip":
        await state.update_data(photo_id=None)
        await _show_summary(message, state)
        return

    if not message.photo:
        await message.answer("Нужно фото или `skip`. Повторите:")
        return

    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)

    await _show_summary(message, state)


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
    elif field == "balance":
        await callback.message.answer("Введите balance (целое число):")
        await state.set_state(UserRegister.balance)
    elif field == "coords":
        await callback.message.answer("Введите `longitude, latitude` или отправьте локацию:")
        await state.set_state(UserRegister.coords)
    elif field == "photo":
        await callback.message.answer("Отправьте фото или `skip`:")
        await state.set_state(UserRegister.photo)
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
        "telegram_id": data["telegram"]["telegram_id"],
        "user": {
            "telegram_info": {
                "id": data["telegram_info"]["id"],
                "telegram_id": data["telegram_info"]["telegram_id"],
                "username": data["telegram_info"]["username"],
                "chat_id": data["telegram_info"]["chat_id"],
            },
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "role": data["role"],
            "balance": data["balance"],
            "longitude": float(data["longitude"]),
            "latitude": float(data["latitude"]),
            "photo_id": data.get("photo_id"),
        }
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
                    await loading.edit_text(f"✅ Успех. Ответ сервера: {result}")
                    await state.clear()
                else:
                    text = await resp.text()
                    await loading.edit_text(f"❌ Ошибка {resp.status}: {text[:500]}")
    except Exception as e:
        await loading.edit_text(f"❌ Ошибка отправки: {e}")
