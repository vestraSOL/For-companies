## Стек

- FastAPI
- SQLAlchemy 2.0 async
- Alembic
- Pydantic v2
- PostgreSQL
- async/await
- SQLAdmin

## Структура проекта

```text
python-backend/
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── domain/
│   ├── integrations/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── .env.example
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Реализованные модули

- `auth` и `profile`
- `users` search
- `federations`
- `companies`
- `projects`
- `tasks`
- `comments`
- `reminders`
- `tags`
- `catalogs`
- `company_fields` и `project_fields`

## Запуск локально

1. Скопировать env-файл и при необходимости поправить подключение к PostgreSQL:

```bash
cp .env .env
```

2. Полный запуск приложения на Python 3.14 и PostgreSQL 18:

```bash
docker-compose up --build
```

Что поднимается:

- `db`: PostgreSQL 18 с volume `postgres_data`
- `app`: FastAPI-приложение, которое перед стартом выполняет `alembic upgrade head`

После старта доступны:

- API docs: `http://localhost:8000/docs`
- Админка: `http://localhost:8000/admin`

Для входа в админку можно использовать уже существующего пользователя. По умолчанию это пользователь `admin@example.com` с паролем `admin`.

Делать миграции и прочие команды:
- `docker-compose exec app alembic revision --autogenerate -m "describe change"`
- `docker-compose exec app pytest`

## Линтеры и pre-commit

Ручной запуск:

Подключить pre-commit:

```bash
pre-commit install
pre-commit run --all-files
```

```bash
ruff check . --fix
ruff format .
mypy
```

## Миграции

- Alembic конфиг: alembic.ini
- Alembic env: alembic/env.py
- Начальная схема: alembic/versions/20260407_0001_initial_schema.py

Создание следующей миграции:

```bash
alembic revision -m "describe change"
```

## ENV-переменные

Основные:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- `APP_HOST`
- `APP_PORT`
- `CORS_ALLOW_ORIGINS`
- `ADMIN_TITLE`
- `ADMIN_BASE_URL`
- `ADMIN_SESSION_SECRET`
- `ADMIN_ALLOWED_EMAILS`
- `BOOTSTRAP_ADMIN_ON_STARTUP`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `BOOTSTRAP_ADMIN_FIRST_NAME`
- `BOOTSTRAP_ADMIN_LAST_NAME`
- `BOOTSTRAP_ADMIN_MIDDLE_NAME`
- `BOOTSTRAP_ADMIN_PHONE`

Плейсхолдеры для будущих заданий:

- `REDIS_URL`
- `KAFKA_BROKERS`
- `ENABLE_METRICS`

## Где продолжать задания

- Новый модуль `legal_entities`: полный шаблон `model + migration + schema + repository + service + router` по аналогии с уже реализованными модулями.
- Новый модуль `bank_account`: ориентироваться по стилю существующих CRUD-модулей и собрать отдельный вертикальный срез.
- Prometheus/Grafana: добавить реальный recorder поверх app/integrations/metrics.py
- Kafka: заменить no-op bus в app/integrations/events.py
- Redis: заменить no-op backend в app/integrations/cache.py
