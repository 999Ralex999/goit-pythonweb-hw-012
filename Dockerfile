FROM python:3.10-slim

# Налаштовуємо змінні середовища для Poetry та шляху до додатку
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    APP_HOME=/app

# Встановлюємо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Оновлюємо pip і встановлюємо poetry
RUN pip install --upgrade pip && pip install poetry

# Копіюємо тільки файли залежностей для кешування шарів
COPY pyproject.toml poetry.lock* ./

# Встановлюємо залежності без створення віртуального оточення
RUN poetry install --no-root --no-interaction

# Копіюємо увесь проєкт у контейнер
COPY . .

# Відкриваємо порт для FastAPI
EXPOSE 8000

# Команда запуску FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
