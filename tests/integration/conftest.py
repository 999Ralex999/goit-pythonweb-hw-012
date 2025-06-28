import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.enum.user_role import UserRole
from main import app
from app.entity.bootstrap import Base, User, Contact
from app.database.db import get_db
from app.services.auth import auth_service
from app.security.password_hasher import password_hasher

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "test",
    "email": "test@test.com",
    "password": "testtest",
    "role": UserRole.USER,
}

test_admin_user = {
    "username": "test_admin",
    "email": "test_admin@test.com",
    "password": "testtest",
    "role": UserRole.ADMIN,
}

today = datetime.now()
safe_birthday = today + timedelta(days=3)

test_contacts = [
    {
        "user_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "birthday": datetime(1990, 1, 1),
        "additional_info": "Test contact 1",
    },
    {
        "user_id": 1,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567891",
        "birthday": datetime(1990, 2, 2),
        "additional_info": "Test contact 2",
    },
    {
        "user_id": 1,
        "first_name": "Bob",
        "last_name": "Wilson",
        "email": "bob.wilson@example.com",
        "phone": "+1234567892",
        "birthday": datetime(1992, 3, 3),
        "additional_info": "Test contact 3",
    },
    {
        "user_id": 1,
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+1234567893",
        "birthday": datetime(1993, safe_birthday.month, safe_birthday.day),
        "additional_info": "Test contact 4",
    },
]


@pytest.fixture(scope="function", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            current_user = User(
                id=1,
                username=test_user["username"],
                email=test_user["email"],
                password=password_hasher.hash_password(test_user["password"]),
                role=test_user["role"],
                email_verified=True,
                avatar="<https://twitter.com/gravatar>",
            )
            admin_user = User(
                id=2,
                username=test_admin_user["username"],
                email=test_admin_user["email"],
                password=password_hasher.hash_password(test_admin_user["password"]),
                role=test_admin_user["role"],
                email_verified=True,
                avatar="<https://twitter.com/gravatar>",
            )
            for contact in test_contacts:
                session.add(
                    Contact(
                        user_id=contact["user_id"],
                        first_name=contact["first_name"],
                        last_name=contact["last_name"],
                        email=contact["email"],
                        phone=contact["phone"],
                        birthday=contact["birthday"],
                        additional_info=contact["additional_info"],
                    )
                )
            session.add(current_user)
            session.add(admin_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="function")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    user = User(username=test_user["username"])
    token = await auth_service.create_access_token(user)
    return token


@pytest_asyncio.fixture()
async def get_refresh_token():
    user = User(username=test_user["username"])
    token = await auth_service.create_refresh_token(user)
    return token


@pytest_asyncio.fixture()
async def get_admin_token():
    user = User(username=test_admin_user["username"])
    token = await auth_service.create_access_token(user)
    return token

