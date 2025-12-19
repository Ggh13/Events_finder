UserMap

https://miro.com/welcomeonboard/SW5tR29DOG5GZy84dGlaWFRmeWdrcTVUd2lzQ3F1UU5zeU0ybnNvUmxBcUFRSWRjTEIxSTlUZ2c5cG1pT2VxWVNFRnZUMjBNcHV2YmgxMUV0R2RMTFpCcTQvRkcwekY1MmFuczMwTkh1QXArOWJ4SkprOWRpd0wvNmRjSktkdktQdGo1ZEV3bUdPQWRZUHQzSGl6V2NBPT0hdjE=?share_link_id=479813658966

##  Хранение файлов в телеграм

### 1. У каждого присылаемого файла уникальный file_id
### 2. Получить информацию о файле
**GET** ``https://api.telegram.org/bot<token>/getFile?file_id=<file_id>``

`token` - Токен бота

`file_id` - Id файла

**Response:**

```json
{
  "ok": true,
  "result": {
    "file_id": "AgACAgIAAxkBAAIBrGk9gZ_3WDbR3LaJF6bQJCH7yJnQAAL1DmsbDyPwSQpwj2vy_RNgAQADAgADcwADNgQ",
    "file_unique_id": "AQAD9Q5rGw8j8El4",
    "file_size": 1152,
    "file_path": "photos/file_24.jpg"
  }
}
```
### 3. Скачать файл
**GET** `https://api.telegram.org/file/bot<token>/<file_path>`

`token` - Токен бота

`file_path` - Путь к файлу (параметр из предыдущего пункта)

**Response (200):** сам файл

##  Общие эндпоинты (для всех ролей)

### 1. Создание аккаунта
**POST** `/api/register`

**Request:**
```json
{
  "telegram_id": 123,
  "user": {
    "telegram_info": {
      "id": 1,
      "telegram_id": 123,
      "username": "ivan_petrov",
      "chat_id": 123
    },
    "first_name": "Ivan",
    "last_name": "Petrov",
    "role": "PARTICIPANT",
    "balance": 0,
    "longitude": 37.6,
    "latitude": 55.7,
    "photo_id": null
  }
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
  "categories": [
    "Машинное обучение",
  ],
  "top_k": 5 
}
```
`categories` может содержать в себе от 1 до 34 строк
`top_k` - количество рекомендуемых категорий, обычно 5
**Response (200):**
```json
{
  "recommendations": [
    "Анализ данных и Big Data",
    "Стажировки",
    "Хакатоны",
    "Глубокое обучение",
    "DevOps"
  ]
}
```


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

---

### 19. Получить предполагаемый канал
**POST** `/api/v1/predict`

**Request:**
```json
{
	"text": "🎄 Новогодний интеллектуальный забег . . . от ACM MISIS!",
	"image":"/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDA . . . zQ5Ojf"
}
```

**Response (201):**
```json
{
	"success": true,
	"predicted_class": "acmmisis",
	"conf": 0.9233613014221191
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
