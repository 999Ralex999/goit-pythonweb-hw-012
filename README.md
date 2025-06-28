## 🧠 Фінальний проект — FastAPI + PostgreSQL + Redis + Docker + JWT

### 📌 Опис проекту

У цьому проекті реалізовано повноцінний REST API на базі FastAPI з підтримкою авторизації через JWT, кешуванням через Redis, зберіганням аватарів у хмарі та з'єднанням з базою даних PostgreSQL. Проект контейнеризований у Docker-середовище для зручного розгортання.

---

Користувач може:

- Реєструватися, логінитися, верифікувати email;
 
- Створювати, переглядати, редагувати та видаляти контакти;

- Зберігати аватар користувача (Cloudinary);

- Отримати контакти з днем народження в межах 7 днів;

- Отримати список контактів з фільтрами за ім’ям, email або номером телефону.

---

### 🛠 Використані технології
- Python 3.10

- FastAPI

- PostgreSQL 14

- Redis

- Docker, Docker Compose

- SQLAlchemy

- Alembic

- Pydantic

- Cloudinary

- Pytest (unit + integration)

- Sphinx (документація)

- HTML/CSS/JS (статичні сторінки)

---

### 🚀 Інструкція зі запуску

1. Клонуйте репозиторій:

- git clone https://github.com/999Ralex999/goit-pythonweb-hw-12.git
- cd goit-pythonweb-hw-012

2. Зберіть та запустіть контейнер:

- docker-compose down -v
- docker-compose up --build

3. Відкрийте у браузері:

- http://localhost:8000

4. API доступне за адресою /docs (Swagger UI)

---

### 📁 Структура проекту

📁 app/ — основна логіка FastAPI

  ├── api/ — маршрути (auth, contacts, users)

  ├── schemas/ — Pydantic-схеми

  ├── models/ — SQLAlchemy-моделі

  ├── services/ — бізнес-логіка (auth, contact, mail, user)

  ├── repository/ — робота з БД

  ├── entity/ — ініціалізація таблиць

  ├── database/ — налаштування PostgreSQL, Redis

  ├── middlewares/ — логування

  ├── exceptions/ — кастомні помилки

📁 tests/ — модульні та інтеграційні тести

📁 migrations/ — Alembic

📄 docker-compose.yml — опис сервісів Docker

📄 Dockerfile — інструкція для створення образу

📄 pyproject.toml — залежності (poetry)

📄 main.py — точка входу

---

### 🧪 Тестування

- Покриття тестами: >83%

- Види тестів: unit, integration

- Команди запуску: 
PYTHONPATH=. pytest --cov=app tests/


---

### 📚 Документація

- Автоматична генерація з docstrings за допомогою Sphinx

- Знаходиться у папці docs/

- Генерація HTML:
cd docs
make html

---

### 📝 Примітка
📦 До .dockerignore та .gitignore додані:

- .venv, __pycache__, poetry.lock, migrations/versions, postgres-data/

- Це дозволяє уникнути потрапляння службових файлів до репозиторію.

---

### 👨‍💻 Автор

Олександр Ребенок

GitHub: https://github.com/999Ralex999
