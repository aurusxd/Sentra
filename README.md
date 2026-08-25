# Sentra

Платформа для автоматизации коммуникаций и внутренних бизнес-процессов: веб-интерфейс, REST API, управление пользователями и диалогами, работа с файлами, интеграции с **Telegram** и **MAX**.

Сайт проекта: [sentra.fun](https://sentra.fun)

---

## Возможности

- 📋 Управление пользователями и ролями, JWT-аутентификация
- 💬 Ведение диалогов (переписок) с клиентами в едином интерфейсе
- 🤖 Интеграция с **Telegram** (через `aiogram`) и мессенджером **MAX** (через `maxapi`)
- 📎 Загрузка и обработка файлов (PDF, DOCX и др.)
- 🧠 Поиск и работа с документами на базе эмбеддингов (LangChain + Chroma) — RAG-подход для ответов на основе загруженных материалов
- 🌐 REST API на FastAPI + веб-интерфейс (landing/фронтенд на Next.js)
- 🐘 Хранение данных в PostgreSQL с миграциями через Alembic

## Технологический стек

**Backend**
- Python 3.13+
- FastAPI, Uvicorn
- SQLAlchemy, Alembic, asyncpg / psycopg
- PostgreSQL
- aiogram (Telegram Bot API)
- maxapi (интеграция с MAX)
- LangChain, Chroma (векторный поиск / RAG)
- PyMuPDF, docx2txt (парсинг документов)
- PyJWT, bcrypt, cryptography (аутентификация и шифрование)
- Loguru (логирование)

**Frontend**
- Next.js
- React
- Tailwind CSS
- Framer Motion
- Lucide Icons

**Инфраструктура**
- Docker / Docker Compose
- systemd-юниты для развёртывания на сервере

## Структура проекта

```
Sentra/
├── backend/           # исходный код backend-части (FastAPI, боты, сервисы)
├── src/                # исходный код фронтенда (Next.js)
├── deploy/systemd/    # unit-файлы для запуска сервисов через systemd
├── docs/               # документация проекта
├── scripts/            # вспомогательные скрипты (например, создание администратора)
├── main.py             # точка входа backend-приложения
├── alembic.ini          # конфигурация миграций базы данных
├── docker-compose.yml   # оркестрация backend, БД и миграций
├── Dockerfile            # сборка образа backend
└── .env.example          # пример файла переменных окружения
```

## Быстрый старт

### Через Docker Compose

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/aurusxd/Sentra.git
   cd Sentra
   ```
2. Скопируйте файл окружения и заполните значения:
   ```bash
   cp .env.example .env
   ```
3. Запустите сервисы:
   ```bash
   docker compose up -d --build
   ```
   Compose поднимет backend (порт `8000`), базу данных PostgreSQL и применит миграции Alembic.

4. (Опционально) создайте администратора:
   ```bash
   python -m backend.scripts.create_admin
   ```
   Используются переменные `BOOTSTRAP_ADMIN_NAME` и `BOOTSTRAP_ADMIN_PASSWORD` из `.env`.

### Локальная разработка (backend)

Проект использует `uv` (см. `uv.lock` и `pyproject.toml`):

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

### Локальная разработка (frontend)

```bash
npm install
npm run dev
```

## Переменные окружения

Основные переменные из `.env.example`:

| Переменная | Назначение |
| --- | --- |
| `TELEGRAM_LEAD_BOT_TOKEN` / `TELEGRAM_LEAD_CHAT_ID` | Бот и чат для уведомлений о заявках с лендинга |
| `JWT_KEY` | Ключ подписи JWT-токенов (минимум 32 символа) |
| `TOKEN_ENCRYPTION_KEY` | Fernet-ключ для шифрования токенов |
| `REGISTRATION_ADMIN_EMAIL` | Email администратора для регистрации |
| `BOOTSTRAP_ADMIN_NAME` / `BOOTSTRAP_ADMIN_PASSWORD` | Данные для создания первого администратора |
| `COOKIE_SECURE` | Флаг безопасных cookie |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` / `POSTGRES_HOST` / `POSTGRES_PORT` | Параметры подключения к PostgreSQL |
| `NEXT_PUBLIC_API_URL` | Публичный адрес backend API для фронтенда |

Полный список — в файле [`.env.example`](.env.example).

## Развёртывание

В каталоге `deploy/systemd` находятся unit-файлы для запуска сервисов на сервере через `systemd`, что позволяет разворачивать проект без Docker при необходимости.

## Документация

Дополнительные материалы находятся в каталоге [`docs`](docs).

## Лицензия

Информация о лицензии в репозитории не указана. Уточните условия использования у автора проекта.
