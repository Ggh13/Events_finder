
##  Общие эндпоинты (для всех ролей)

### 1. Создание аккаунта
**POST** `/api/create_account`

**Request:**
```json
{
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "chat_id": 987654321,
  "longitude": 37.622504,
  "latitude": 55.753215,
  "role": "P"
}
```

**Response (200):**


---

### 2. Добавить категорию интересов
**POST** `/api/add_category`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "success": true,
  "message": "Categories added successfully",
  "data": {
    "user_id": 1,
    "categories": [
      {
        "id": 1,
        "name": "Спорт"
      },
      {
        "id": 2,
        "name": "Музыка"
      },
      {
        "id": 3,
        "name": "Технология"
      }
    ]
  }
}
```

**Response (200):**



### 3. Удалить категорию интересов
**DELETE** `/api/delete_category`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "data": {
    "user_id": 1,
    "removed_category_id": 2
  }
}
```

**Response (200):**


---

### 4. Просмотр событий (с фильтрацией)
**GET** `/api/view_events`


**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "data": {
    "total": 50,
    "limit": 20,
    "offset": 0,
    "events": [
      {
        "id": 1,
        "name": "Марафон по программированию",
        "description": "Соревнование для разработчиков",
        "date": "2025-12-15T14:00:00Z",
        "address": "Москва, ул. Тверская, 1",
        "location": {
          "longitude": 37.622504,
          "latitude": 55.753215
        },
        "age_restriction": 18,
        "chat_link": "https://t.me/marathon_2025",
        "organiser": {
          "id": 5,
          "first_name": "Alice",
          "last_name": "Smith",
          "photo_url": "https://example.com/photo.jpg"
        },
        "max_participants": 100,
        "current_participants": 45,
        "cost": 500,
        "status": "active",
        "categories": [
          {
            "id": 1,
            "name": "Технология"
          }
        ],
        "photos": [
          {
            "id": 1,
            "url": "https://example.com/event1.jpg"
          }
        ],
        "distance_km": 2.5
      }
    ]
  }
}
```

---



## Эндпоинты для Дистрибьютора (Distributor)

### 6. Просмотр рекомендаций
**GET** `/api/view_recommendations`

**Headers:** `Authorization: Bearer {token}`


**Response (200):**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": 1,
        "event_id": 1,
        "event_name": "Марафон по программированию",
        "recommended_to_user_id": 2,
        "recommended_to_user": {
          "id": 2,
          "first_name": "Bob",
          "last_name": "Johnson"
        },
        "reason": "Matches your interests in Technology",
        "confidence_score": 0.95,
        "created_at": "2025-12-10T20:42:00Z"
      }
    ]
  }
}
```

---

## Эндпоинты для Креатора (Organiser)

### 7. Создать событие
**POST** `/api/create_event`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "organiser_id": 5,
  "name": "Марафон по программированию",
  "description": "Соревнование для разработчиков на скорость",
  "date": "2025-12-15T14:00:00Z",
  "address": "Москва, ул. Тверская, 1",
  "location": {
    "longitude": 37.622504,
    "latitude": 55.753215
  },
  "age_restriction": 18,
  "chat_link": "https://t.me/marathon_2025",
  "max_participants": 100,
  "cost": 500,
  "category_ids": [1, 3],
  "photo_ids": [1, 2, 3]
}
```

**Response (201):**


---

### 8. Редактировать событие
**PUT** `/api/edit_event/:id_event`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "name": "Марафон по программированию 2025",
  "description": "Обновленное описание",
  "date": "2025-12-16T14:00:00Z",
  "address": "Москва, ул. Тверская, 5",
  "location": {
    "longitude": 37.625000,
    "latitude": 55.755000
  },
  "age_restriction": 16,
  "chat_link": "https://t.me/marathon_2025_updated",
  "max_participants": 150,
  "cost": 600,
  "category_ids": [1, 3, 4]
}
```

**Response (200):**


---

### 9. Просмотр своих событий
**GET** `/api/view_my_events`

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total": 12,
    "limit": 20,
    "offset": 0,
    "events": [
      {
        "id": 1,
        "name": "Марафон по программированию",
        "description": "Соревнование для разработчиков",
        "date": "2025-12-15T14:00:00Z",
        "address": "Москва, ул. Тверская, 1",
        "status": "active",
        "max_participants": 100,
        "current_participants": 45,
        "cost": 500,
        "balance": 22500,
        "is_freezed": false,
        "created_at": "2025-12-01T10:00:00Z",
        "updated_at": "2025-12-10T20:42:00Z",
        "categories": [
          {
            "id": 1,
            "name": "Технология"
          }
        ]
      }
    ]
  }
}
```

---

### 10. Удалить событие
**DELETE** `/api/delete_event/:id_event`

**Headers:** `Authorization: Bearer {token}`

**Response (200):**

---

## Эндпоинты для Админа (Admin)

### 11. Добавить креатора (Organiser)
**POST** `/api/add_creator`

**Headers:** `Authorization: Bearer {admin_token}`

// Денис говорил, что мы теперь храним токены, хз правильно так делать или нет

**Request:**
```json
{
  "user_id": 10,
}
```

**Response (200):**

---

### 12. Удалить креатора (Downgrade Organiser)
**DELETE** `/api/delete_creator`

**Headers:** `Authorization: Bearer {admin_token}`

**Request:**
```json
{
  "user_id": 10,
}
```

**Response (200):**
---

### 16. Получить профиль пользователя
**GET** `/api/users/:user_id`

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "telegram_id": 123456789,
    "first_name": "John",
    "last_name": "Doe",
    "balance": 1500,
    "role": "P",
    "location": {
      "longitude": 37.622504,
      "latitude": 55.753215
    },
    "photo": {
      "id": 1,
      "url": "https://example.com/photo.jpg"
    },
    "categories": [
      {
        "id": 1,
        "name": "Спорт"
      }
    ],
    "teams": [
      {
        "id": 1,
        "name": "Team A"
      }
    ],
    "created_at": "2025-12-01T10:00:00Z"
  }
}
```

---

### 17. Пожаловаться на пользователя
**POST** `/api/users/:user_id/report`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "sender_id": 2,
  "message": "Inappropriate behavior during the event"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Report submitted successfully",
  "data": {
    "report_id": "550e8400-e29b-41d4-a716-446655440001",
    "reported_user_id": 5,
    "created_at": "2025-12-10T20:42:00Z"
  }
}
```

---

### 18. Пожаловаться на событие
**POST** `/api/events/:id_event/report`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "sender_id": 2,
  "message": "Event description contains inappropriate content"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Report submitted successfully",
  "data": {
    "report_id": "550e8400-e29b-41d4-a716-446655440002",
    "reported_event_id": 1,
    "created_at": "2025-12-10T20:42:00Z"
  }
}
```





## Роли пользователей

| Роль | Код | Права |
|------|------|-------|
| Участник | P | Просмотр событий, подача заявок |
| Админ | A | Управление крейторами |
| Крейтор | O | Создание и редактирование событий |
| Дистрибьютор | D | Просмотр рекомендаций |
=======
# Events_finder

http://62.113.43.6/api/health
