# SULTAN — Система учёта тренировочных нагрузок

## Стек
- Python 3.13, Django 5.x, PostgreSQL 16
- Bootstrap 5 (CDN)
- openpyxl (Excel-отчёты)
- aiogram 3.x (Telegram-бот)

## Быстрый старт

### 1. Клонирование и виртуальное окружение

```bash
cd sultan
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
```

Откройте `.env` и заполните параметры:

```
SECRET_KEY=ваш-случайный-ключ
DEBUG=True
DB_NAME=sultan_db
DB_USER=postgres
DB_PASSWORD=ваш-пароль
DB_HOST=localhost
DB_PORT=5432
TELEGRAM_BOT_TOKEN=токен-от-@BotFather
LOCK_DAYS=30
```

### 3. Создание базы данных PostgreSQL

```sql
-- psql -U postgres
CREATE DATABASE sultan_db ENCODING 'UTF8' LC_COLLATE 'ru_RU.UTF-8' LC_CTYPE 'ru_RU.UTF-8' TEMPLATE template0;
```

Если locale `ru_RU.UTF-8` недоступен:

```sql
CREATE DATABASE sultan_db ENCODING 'UTF8';
```

### 4. Применение миграций

```bash
python manage.py makemigrations core
python manage.py migrate
```

### 5. Заполнение начальными данными

```bash
python manage.py seed_data
```

Будут созданы:

| Логин | Пароль | Роль |
|-------|--------|------|
| `admin` | `admin123` | Администратор |
| `trainer_иванов` | `trainer123` | Тренер |
| `trainer_петрова` | `trainer123` | Тренер |
| `athlete_1` | `athlete123` | Атлет |
| `athlete_2` | `athlete123` | Атлет |

> ⚠️ **Смените пароли после первого входа!**

### 6. Запуск Django-сервера

```bash
python manage.py runserver
```

Откройте браузер: http://127.0.0.1:8000/

### 7. Запуск Telegram-бота

В отдельном терминале:

```bash
cd bot
python main.py
```

---

## Структура проекта

```
sultan/
├── sultan/          — настройки Django
├── core/            — основное приложение (модели, views, формы)
│   ├── models.py    — все 7 моделей
│   ├── views/       — views по роли
│   ├── forms.py     — формы с валидацией
│   ├── decorators.py — role_required
│   └── management/commands/
│       ├── seed_data.py        — начальные данные
│       ├── backup_db.py        — SQL-дамп
│       └── lock_old_trainings.py — блокировка старых записей
├── reports/         — подсистема отчётов (Excel/openpyxl)
├── bot/             — Telegram-бот (aiogram 3.x)
├── templates/       — HTML-шаблоны (Bootstrap 5)
├── static/css/      — sultan.css
├── backups/         — SQL-дампы (создаются автоматически)
├── media/reports/   — сгенерированные Excel-файлы
└── requirements.txt
```

---

## Management-команды

### Резервное копирование БД

```bash
python manage.py backup_db
# Файл: backups/sultan_YYYY-MM-DD.sql
```

**Автоматический бэкап через cron (ежедневно в 3:00):**

```cron
0 3 * * * /path/to/venv/bin/python /path/to/sultan/manage.py backup_db
```

### Блокировка старых записей

```bash
# Заблокировать тренировки старше 30 дней
python manage.py lock_old_trainings

# Указать другое количество дней
python manage.py lock_old_trainings --days 60

# Проверка без изменений
python manage.py lock_old_trainings --dry-run
```

**Автоматически через cron (ежедневно в 2:00):**

```cron
0 2 * * * /path/to/venv/bin/python /path/to/sultan/manage.py lock_old_trainings
```

---

## Роли и права доступа

| Функция | Admin | Trainer | Athlete |
|---------|-------|---------|---------|
| Просмотр всех тренировок | ✓ | Только своих атлетов | Только свои |
| Добавление тренировки | ✓ | ✓ | — |
| Редактирование тренировки | ✓ (в т.ч. заблокированных) | Только незаблокированных | — |
| Управление атлетами | ✓ | ✓ | — |
| Управление упражнениями | ✓ | ✓ | — |
| Генерация отчётов | ✓ | ✓ | Только личные |
| Управление пользователями | ✓ | — | — |
| Разблокировка записей | ✓ | — | — |

---

## Привязка Telegram-аккаунта

Бот ищет пользователя по `username = 'tg_<telegram_id>'`.

Чтобы привязать пользователя:

1. Узнайте Telegram ID (например, через @userinfobot)
2. В Django Admin измените `username` нужного User на `tg_<telegram_id>`
   (например, `tg_123456789`)

---

## Поддерживаемые браузеры

Chrome 120+, Safari 17+, Firefox 121+  
Минимальное разрешение: 1280×720
