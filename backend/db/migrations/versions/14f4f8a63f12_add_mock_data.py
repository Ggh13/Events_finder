"""Add mock data

Revision ID: 14f4f8a63f12
Revises: 1dabc852f944
Create Date: 2025-12-12 21:20:48.453837

"""
from typing import Sequence, Union

import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '14f4f8a63f12'
down_revision: Union[str, Sequence[str], None] = '1dabc852f944'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    photo_table = table(
        'photo',
        column('url', sa.Text()),
        schema='events_finder'
    )

    photos = [
        { "url": "https://m.media-amazon.com/images/M/MV5BOTczZDk5NWEtOWExMi00M2RiLWEzN2ItMDBkY2ExMzBhMTczXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"},
        { "url": "https://cdn.forbes.ru/files/c/998x924/profile/ramzan_kadyrov_2018-06-15_02.jpg__1625147202__19904.webp"},
        { "url": "https://cdnn21.img.ria.ru/images/07e7/03/11/1858711565_0:81:3070:1808_1920x0_80_0_0_2eb7d6ae99657af24a2e7fe6901f9dc9.jpg"},
        {"url": "https://blog.ikraikra.ru/wp-content/uploads/2024/08/FNR_9643-1536x1024.jpg"},
        {"url": "https://interesnyefakty.org/wp-content/uploads/chto-takoe-hakaton.jpg"},
        {"url": "https://ru.hexlet.io/tp/versions/621750928469/tild3533-3633-4632-b866-656262613365__screenshot_28.png"},
        {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSR44pJmtu_d2r2oDs1Nd4FmtxpaQr6_Cf3CQ&s"},
        {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRXaCK_vIdW1VN-D6XMmG-ivJ_gCiktMGyZbA&s"},
        {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQzi8L3egO95Ya0oXXobyMS3rT1T2ZsgdBqDg&s"},
<<<<<<< HEAD
        {"url": "https://img03.rl0.ru/afisha/e1200x800i/daily.afisha.ru/uploads/images/3/8b/38b74343840e21c54359d3fa7018c941.jpg"},
=======
>>>>>>> 5ca659b (feat(migrations): add mock data)
    ]

    op.bulk_insert(photo_table, photos)

    tg_table = table(
        'telegram_info',
        column('telegram_id', sa.BigInteger()),
        column('username', sa.Text()),
        column('chat_id', sa.BigInteger()),
        schema='events_finder'
    )
    tg_info = [
        { "telegram_id": 1050682049,  "username": "gachimansemen","chat_id": 1050682049,},
        { "telegram_id": 5018845956,  "username": "BRDDRTy","chat_id": 5018845956,},
        { "telegram_id": 1041714664,  "username": "C4eboksar","chat_id": 1041714664,},
<<<<<<< HEAD
        { "telegram_id": 839846696,  "username": "germanpikel","chat_id": 839846696,},
=======
>>>>>>> 5ca659b (feat(migrations): add mock data)
    ]
    op.bulk_insert(tg_table, tg_info)


    user_table = table(
        'user',
        column('telegram_id', sa.Integer()),
        column('first_name', sa.Text()),
        column('last_name', sa.Text()),
        column('photo_id', sa.Integer()),
        column('balance', sa.Integer()),
        column('role', postgresql.ENUM('PARTICIPANT', 'ADMIN', 'ORGANISER', 'DISTRIBUTOR', name='user_role')),
        column('longitude', sa.DECIMAL(precision=8, scale=6)),
        column('latitude', sa.DECIMAL(precision=9, scale=6)),
        schema='events_finder'
    )

    users = [
        {"first_name": "Semyon", "last_name": "Anikin", "telegram_id": 1, "photo_id": 1,
          "balance": 0, "role": "ORGANISER", "longitude": 55.75, "latitude": 37.62},
        {"first_name": "Roman", "last_name": "Buzhor", "telegram_id": 2, "photo_id": 2,
          "balance": 0, "role": "DISTRIBUTOR", "longitude": 55.75, "latitude": 37.62},
        {"first_name": "Denis", "last_name": "Tugov", "telegram_id": 3, "photo_id": 3,
          "balance": 0, "role": "ADMIN", "longitude": 55.75, "latitude": 37.62},
<<<<<<< HEAD
        {"first_name": "German", "last_name": "Pickel", "telegram_id": 4, "photo_id": 10,
          "balance": 0, "role": "PARTICIPANT", "longitude": 55.75, "latitude": 37.62},
=======
>>>>>>> 5ca659b (feat(migrations): add mock data)
    ]
    
    op.bulk_insert(user_table, users)

    event_table = table(
        'event',
        column('name', sa.Text()),
        column('description', sa.Text()),
        column('date', sa.DateTime()),
        column('address', sa.Text()),
        column('longitude', sa.DECIMAL(precision=8, scale=6)),
        column('latitude', sa.DECIMAL(precision=9, scale=6)),
        column('age_restriction', sa.Integer()),
        column('chat_link', sa.Text()),
        column('organiser_id', sa.Integer()),
        column('max_participants', sa.Integer()),
        column('cost', sa.Integer()),
        column('balance', sa.Integer()),
        column('is_freezed', sa.Boolean()),
        schema='events_finder'
    )

    events = [
        {
            "name": "Хакатон по машинному обучению",
            "description": "48-часовой хакатон для разработчиков ML-решений. Призы от спонсоров, менторство от экспертов индустрии.",
            "date": datetime.datetime.fromisoformat("2024-06-15T10:00:00"),
            "address": "Москва, Ленинский проспект, 4",
            "longitude": 55.7097,
            "latitude": 37.5788,
            "age_restriction": 16,
            "chat_link": "https://t.me/+abcdef123456",
            "organiser_id": 1,
            "max_participants": 100,
            "cost": 0,
            "balance": 50000,
            "is_freezed": False
        },
        {
            "name": "Воркшоп по Backend-разработке на Python",
            "description": "Практический воркшоп по созданию высоконагруженных backend-систем. Рассмотрим FastAPI, асинхронность, базы данных.",
            "date": datetime.datetime.fromisoformat("2024-05-20T18:30:00"),
            "address": "Москва, ул. Малая Пироговская, 1",
            "longitude": 55.7317,
            "latitude": 37.5749,
            "age_restriction": 18,
            "chat_link": "https://t.me/+ghijkl789012",
            "organiser_id": 1,
            "max_participants": 50,
            "cost": 1500,
            "balance": 30000,
            "is_freezed": False
        },
        {
            "name": "Кибербезопасность для начинающих",
            "description": "Введение в основы кибербезопасности. Практические задания по защите веб-приложений и сетей.",
            "date": datetime.datetime.fromisoformat("2024-07-10T14:00:00"),
            "address": "Москва, Кремль, 1",
            "longitude": 55.7520,
            "latitude": 37.6176,
            "age_restriction": 18,
            "chat_link": "https://t.me/+mnopqr345678",
            "organiser_id": 1,
            "max_participants": 75,
            "cost": 0,
            "balance": 20000,
            "is_freezed": False
        },
        {
            "name": "Спортивное программирование: подготовка к олимпиадам",
            "description": "Регулярные тренировки по спортивному программированию. Разбор задач с Codeforces, LeetCode.",
            "date": datetime.datetime.fromisoformat("2024-05-25T16:00:00"),
            "address": "Москва, Мичуринский проспект, 1",
            "longitude": 55.6998,
            "latitude": 37.4823,
            "age_restriction": 14,
            "chat_link": "https://t.me/+stuvwx901234",
            "organiser_id": 1,
            "max_participants": 40,
            "cost": 500,
            "balance": 15000,
            "is_freezed": False
        },
        {
            "name": "DevOps Day: CI/CD и контейнеризация",
            "description": "Полный день погружения в DevOps практики. Docker, Kubernetes, GitLab CI на реальных примерах.",
            "date": datetime.datetime.fromisoformat("2024-06-05T11:00:00"),
            "address": "Москва, Пресненская набережная, 8",
            "longitude": 55.7480,
            "latitude": 37.5365,
            "age_restriction": 18,
            "chat_link": "https://t.me/+yzabcd567890",
            "organiser_id": 1,
            "max_participants": 60,
            "cost": 2000,
            "balance": 40000,
            "is_freezed": False
        }
    ]

    op.bulk_insert(event_table, events)


    event_photo_table = table(
        'event_photo',
        column('event_id', sa.Integer()),
        column('photo_id', sa.Integer()),
        schema='events_finder'
    )

    event_photos = [
        # Эвент 1: 2 фото
        {"event_id": 1, "photo_id": 4},
        {"event_id": 1, "photo_id": 5},
        # Эвент 2: 1 фото
        {"event_id": 2, "photo_id": 6},
        # Эвент 3: 1 фото
        {"event_id": 3, "photo_id": 7},
        # Эвент 4: 1 фото
        {"event_id": 4, "photo_id": 8},
        # Эвент 5: 1 фото
        {"event_id": 5, "photo_id": 9},
    ]

    op.bulk_insert(event_photo_table, event_photos)


        # Добавляем еще фото для новых событий
    sport_art_photos = [
        {"url": "https://example.com/events/basketball_tournament.jpg"},
        {"url": "https://example.com/events/basketball_action.jpg"},
        {"url": "https://example.com/events/art_exhibition.jpg"},
        {"url": "https://example.com/events/painting_workshop.jpg"},
    ]
    
    op.bulk_insert(photo_table, sport_art_photos)

    # ### Добавляем спортивное событие ###
    
    # Получаем следующий ID для события (предполагаем, что предыдущих было 5)
    sport_event = {
        "name": "Баскетбольный турнир MISIS Cup",
        "description": "Ежегодный студенческий баскетбольный турнир между факультетами. Призы победителям, развлекательная программа, фуршет. Регистрация команд до 30 мая.",
        "date": datetime.datetime.fromisoformat("2024-06-08T11:00:00"),
        "address": "Москва, Ленинский проспект, 4, Спортивный комплекс НИТУ МИСИС",
        "longitude": 55.7095,
        "latitude": 37.5792,
        "age_restriction": 16,
        "chat_link": "https://t.me/+basketball_misis_cup",
        "organiser_id": 1,  # Семён как организатор
        "max_participants": 120,
        "cost": 0,
        "balance": 25000,
        "is_freezed": False
    }
    
    # Вставляем спортивное событие
    op.bulk_insert(event_table, [sport_event])
    
    # ### Добавляем творческое событие ###
    
    art_event = {
        "name": "Выставка современного искусства 'Молодые таланты'",
        "description": "Выставка работ студентов художественных специальностей. Живопись, графика, цифровое искусство. В рамках выставки пройдут мастер-классы от известных художников и арт-дискуссии.",
        "date": datetime.datetime.fromisoformat("2024-05-28T17:00:00"),
        "address": "Москва, ул. Малая Пироговская, 1, Выставочный зал НИТУ МИСИС",
        "longitude": 55.7315,
        "latitude": 37.5752,
        "age_restriction": 12,
        "chat_link": "https://t.me/+art_exhibition_misis",
        "organiser_id": 1,  # Семён как организатор
        "max_participants": 200,
        "cost": 300,  # Символическая плата за вход
        "balance": 15000,
        "is_freezed": False
    }
    
    # Вставляем творческое событие
    op.bulk_insert(event_table, [art_event])

    # ### Связываем новые события с категориями ###
    
    event_category_table = table(
        'event_category',
        column('event_id', sa.Integer()),
        column('category_id', sa.Integer()),
        schema='events_finder'
    )

    event_categories = [
        # Эвент 1: Хакатон по машинному обучению (ID: 1)
        {"event_id": 1, "category_id": 15},  # Хакатоны (15 в списке)
        {"event_id": 1, "category_id": 6},   # Backend-разработка (6 в списке)
        {"event_id": 1, "category_id": 25},  # Машинное обучение (25 в списке)
        {"event_id": 1, "category_id": 5},   # Глубокое обучение (5 в списке)
        
        # Эвент 2: Воркшоп по Backend-разработке (ID: 2)
        {"event_id": 2, "category_id": 6},   # Backend-разработка
        {"event_id": 2, "category_id": 31},  # Анализ данных и Big Data (31 в списке)
        
        # Эвент 3: Кибербезопасность для начинающих (ID: 3)
        {"event_id": 3, "category_id": 33},  # Кибербезопасность (33 в списке)
        {"event_id": 3, "category_id": 6},   # Backend-разработка
        
        # Эвент 4: Спортивное программирование (ID: 4)
        {"event_id": 4, "category_id": 28},  # Спортивное программирование (28 в списке)
        {"event_id": 4, "category_id": 6},   # Backend-разработка
        
        # Эвент 5: DevOps Day (ID: 5)
        {"event_id": 5, "category_id": 12},  # DevOps (12 в списке)
        {"event_id": 5, "category_id": 6},   # Backend-разработка
        {"event_id": 5, "category_id": 31},  # Анализ данных и Big Data
        
        # Эвент 6: Баскетбольный турнир MISIS Cup (ID: 6)
        {"event_id": 6, "category_id": 34},  # Спорт (34 в списке)
        {"event_id": 6, "category_id": 24},  # Танцы (24 в списке)
        
        # Эвент 7: Выставка современного искусства (ID: 7)
        {"event_id": 7, "category_id": 26},  # Творчество (26 в списке)
        {"event_id": 7, "category_id": 35},  # Дизайн (39 в списке, последний элемент)
        {"event_id": 7, "category_id": 10},  # Музыка (10 в списке)
        {"event_id": 7, "category_id": 17},  # Вокал (17 в списке)
        {"event_id": 7, "category_id": 27},  # Театр (27 в списке)
    ]

    op.bulk_insert(event_category_table, event_categories)

    # ### Связываем новые события с фотографиями ###
    
    # Предполагаем, что ID новых фото начинаются с 10 (4-9 уже заняты)
    new_event_photos = [
        # Спортивное событие (ID 6): 2 фото
        {"event_id": 6, "photo_id": 10},
        {"event_id": 6, "photo_id": 11},
        # Творческое событие (ID 7): 2 фото
        {"event_id": 7, "photo_id": 12},
        {"event_id": 7, "photo_id": 13},
    ]
    
    op.bulk_insert(event_photo_table, new_event_photos)


    user_team_table = table(
        "user_team", 
        column('user_id', sa.Integer()),
        column('team_id', sa.Integer()),
        schema='events_finder'
    )

    distributor_teams = [
        {"user_id": 2, "team_id": 1},  # acmmisis
        {"user_id": 2, "team_id": 2},  # aiknowledgeclub
        {"user_id": 2, "team_id": 3},  # art_klaster
        {"user_id": 2, "team_id": 4},  # itatmisis
        {"user_id": 2, "team_id": 5},  # nust_misis
        {"user_id": 2, "team_id": 6},  # sportmisis
        {"user_id": 2, "team_id": 7},  # youthmisis
    ]
    
    op.bulk_insert(user_team_table, distributor_teams)


    user_category_table = table(
        'user_category',
        column('user_id', sa.Integer()),
        column('category_id', sa.Integer()),
        schema='events_finder'
    )

    user_categories = [
        # Семён (организатор, user_id: 1) - 3 категории:
        {"user_id": 1, "category_id": 6},   # Backend-разработка
        {"user_id": 1, "category_id": 25},  # Машинное обучение
        {"user_id": 1, "category_id": 28},  # Спортивное программирование
        
        # Роман (дистрибьютор, user_id: 2) - 3 категории:
        {"user_id": 2, "category_id": 12},  # DevOps
        {"user_id": 2, "category_id": 33},  # Кибербезопасность
        {"user_id": 2, "category_id": 15},  # Хакатоны
        
        # Денис (админ, user_id: 3) - 3 категории:
        {"user_id": 3, "category_id": 6},   # Backend-разработка
        {"user_id": 3, "category_id": 31},  # Анализ данных и Big Data
        {"user_id": 3, "category_id": 12},  # DevOps

        # Денис (админ, user_id: 3) - 3 категории:
        {"user_id": 4, "category_id": 22},   # Backend-разработка
        {"user_id": 4, "category_id": 31},  # Анализ данных и Big Data
        {"user_id": 4, "category_id": 24},  # DevOps
    ]

    op.bulk_insert(user_category_table, user_categories)



def downgrade() -> None:
    """Downgrade schema."""

    op.execute(text("TRUNCATE TABLE events_finder.user RESTART IDENTITY"))
    op.execute(text("TRUNCATE TABLE events_finder.photo  RESTART IDENTITY"))
    op.execute(text("TRUNCATE TABLE events_finder.telegram_info  RESTART IDENTITY"))
