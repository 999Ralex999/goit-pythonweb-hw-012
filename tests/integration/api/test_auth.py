from unittest.mock import Mock, patch

import pytest
from sqlalchemy import select

from app.security.token_encoder import token_encoder
from app.services.auth import auth_service
from app.security.password_hasher import password_hasher
from app.entity.bootstrap import User
from tests.integration.conftest import TestingSessionLocal, test_admin_user, test_user


@pytest.mark.parametrize(
    "user_data, response_data",
    [
        pytest.param(
            {
                "username": "string",
                "email": "user@example.com",
                "password": "stringst",
                "role": "USER",
            },
            {
                "id": 3,
                "username": "string",
                "email": "user@example.com",
                "role": "USER",
            },
            id="User signup",
        ),
        pytest.param(
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "stringst",
                "role": "ADMIN",
            },
            {
                "id": 3,
                "username": "admin",
                "email": "admin@example.com",
                "role": "ADMIN",
            },
            id="Admin signup",
        ),
    ],
)
def test_signup(client, monkeypatch, user_data, response_data):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    data = response.json()

    assert response.status_code == 201, response.text
    for key, value in response_data.items():
        assert data[key] == value

    mock_send_email.assert_called_once()
    assert mock_send_email.call_args[0][0].to == [user_data["email"]]
    assert mock_send_email.call_args[0][0].subject == "Confirm your email"
    assert mock_send_email.call_args[0][0].data["username"] == user_data["username"]
    assert mock_send_email.call_args[0][0].template == "verify_email.html"

    assert "password" not in data


@pytest.mark.parametrize(
    "user_data, response_data",
    [
        pytest.param(
            {
                "username": "string",
                "email": "test@test.com",
                "password": "stringst",
                "role": "USER",
            },
            {
                "detail": "User with this email already exists",
            },
            id="User with existing email signup",
        ),
        pytest.param(
            {
                "username": "test",
                "email": "user_new@example.com",
                "password": "stringst",
                "role": "USER",
            },
            {
                "detail": "User with this username already exists",
            },
            id="User with existing username signup",
        ),
    ],
)
def test_signup_existing(client, monkeypatch, user_data, response_data):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    data = response.json()

    assert response.status_code == 409, response.text
    for key, value in response_data.items():
        assert data[key] == value

    assert "password" not in data


@pytest.mark.parametrize(
    "user_data, response_code, violations",
    [
        pytest.param(
            {
                "username": "",
                "email": "user@example.com",
                "password": "stringst",
                "role": "USER",
            },
            422,
            [
                {
                    "type": "string_too_short",
                    "loc": ["body", "username"],
                    "msg": "String should have at least 3 characters",
                    "input": "",
                    "ctx": {"min_length": 3},
                }
            ],
            id="Empty username validation",
        ),
        pytest.param(
            {
                "username": "ab",
                "email": "user@example.com",
                "password": "stringst",
                "role": "USER",
            },
            422,
            [
                {
                    "type": "string_too_short",
                    "loc": ["body", "username"],
                    "msg": "String should have at least 3 characters",
                    "input": "ab",
                    "ctx": {"min_length": 3},
                }
            ],
            id="Short username validation",
        ),
        pytest.param(
            {
                "username": "validuser",
                "email": "invalid-email",
                "password": "stringst",
                "role": "USER",
            },
            422,
            [
                {
                    "type": "value_error",
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: An email address must have an @-sign.",
                    "input": "invalid-email",
                }
            ],
            id="Invalid email validation",
        ),
        pytest.param(
            {
                "username": "validuser",
                "email": "user@example.com",
                "password": "short",
                "role": "USER",
            },
            422,
            [
                {
                    "type": "string_too_short",
                    "loc": ["body", "password"],
                    "msg": "String should have at least 8 characters",
                    "input": "short",
                    "ctx": {"min_length": 8},
                }
            ],
            id="Short password validation",
        ),
    ],
)
def test_signup_validator(client, monkeypatch, user_data, response_code, violations: list):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    data = response.json()

    assert response.status_code == response_code, response.text
    assert "detail" in data

    detail = data["detail"]
    assert len(detail) == len(violations)

    for i, violation in enumerate(violations):
        for key, expected_value in violation.items():
            assert detail[i][key] == expected_value, f"Mismatch in violation {i}, key {key}"


def test_get_me(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("api/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


def test_me_unauthorized(client, monkeypatch):
    response = client.get("api/auth/me")
    data = response.json()

    assert response.status_code == 401, response.text
    assert data["detail"] == "Not authenticated"


@patch("app.services.upload_file.UploadFileService.upload_file")
def test_update_avatar_user(mock_upload_file, client, get_admin_token):
    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url
    headers = {"Authorization": f"Bearer {get_admin_token}"}

    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}
    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["username"] == test_admin_user["username"]
    assert data["email"] == test_admin_user["email"]
    assert data["avatar"] == fake_url
    assert data["role"] == "ADMIN"

    mock_upload_file.assert_called_once()


def test_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": test_user.get("username"),
            "password": test_user.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.parametrize(
    "username, password, response_data",
    [
        pytest.param(
            test_user.get("username"),
            "password",
            {"detail": "Invalid credentials"},
            id="Wrong password",
        ),
        pytest.param(
            "username",
            test_user.get("password"),
            {"detail": "Invalid credentials"},
            id="Wrong username",
        ),
        pytest.param(
            "1",
            "1",
            {"detail": "Invalid credentials"},
            id="Wrong username",
        ),
    ],
)
def test_wrong_credentials_login(client, username, password, response_data):
    response = client.post(
        "api/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == response_data["detail"]


@pytest.mark.asyncio
async def test_refresh_token(client, get_refresh_token):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.refresh_token = get_refresh_token
            await session.commit()

    response = client.post(
        "api/auth/refresh_token",
        json={"refresh_token": get_refresh_token},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] == get_refresh_token


def test_refresh_token_invalid(client):
    response = client.post(
        "api/auth/refresh_token",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Token is invalid"


def test_refresh_token_empty(client):
    response = client.post(
        "api/auth/refresh_token",
        json={"refresh_token": ""},
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert len(data["detail"]) == 1
    assert data["detail"][0]["type"] == "string_too_short"
    assert data["detail"][0]["loc"] == ["body", "refresh_token"]
    assert data["detail"][0]["msg"] == "String should have at least 1 character"
    assert data["detail"][0]["input"] == ""
    assert data["detail"][0]["ctx"] == {"min_length": 1}


@pytest.mark.asyncio
async def test_confirm_email_success(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.email_verified = False
            await session.commit()

    email_token = await token_encoder.create_token({"sub": test_user.get("email")})
    response = client.get(
        f"/api/auth/confirmed_email/{email_token}",
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"

    async with TestingSessionLocal() as session:
        user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        user = user.scalar_one_or_none()
        assert user is not None
        assert user.email_verified is True


@pytest.mark.asyncio
async def test_confirm_email_on_confirmed_user(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            assert current_user.email_verified is True

    email_token = await token_encoder.create_token({"sub": test_user.get("email")})
    response = client.get(
        f"/api/auth/confirmed_email/{email_token}",
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"

    async with TestingSessionLocal() as session:
        user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        user = user.scalar_one_or_none()
        assert user is not None
        assert user.email_verified is True


def test_confirm_email_on_invalid_token(client):
    email_token = "invalid_token"
    response = client.get(
        f"/api/auth/confirmed_email/{email_token}",
    )
    data = response.json()

    assert response.status_code == 400, response.text
    assert data["detail"] == "Token is invalid"


@pytest.mark.asyncio
async def test_confirm_email_on_expired_token(client):
    email_token = await token_encoder.create_token(
        {"sub": test_user.get("email")}, expires_delta=-100
    )
    response = client.get(
        f"/api/auth/confirmed_email/{email_token}",
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Token is invalid"


@pytest.mark.asyncio
async def test_resend_verification_email(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.email_verified = False
            await session.commit()

    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "api/auth/resend_verification_email",
        json={"email": test_user.get("email")},
    )

    mock_send_email.assert_called_once()

    mail = mock_send_email.call_args[0][0]
    assert mail.to == [test_user.get("email")]
    assert mail.subject == "Confirm your email"
    assert mail.data["username"] == test_user.get("username")
    assert mail.template == "verify_email.html"

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Verification email sent"


@pytest.mark.asyncio
async def test_resend_verification_email_on_confirmed_user(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.email_verified = True
            await session.commit()

    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "api/auth/resend_verification_email",
        json={"email": test_user.get("email")},
    )

    mock_send_email.assert_not_called()

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email already verified"


def test_resend_verification_email_on_unregistered_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "api/auth/resend_verification_email",
        json={"email": "unregistered_user@example.com"},
    )

    mock_send_email.assert_not_called()

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Verification email sent"


def test_request_password_reset(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "/api/auth/request_password_reset",
        json={"email": test_user.get("email")},
    )

    mock_send_email.assert_called_once()

    mail = mock_send_email.call_args[0][0]
    assert mail.to == [test_user.get("email")]
    assert mail.subject == "Password reset"
    assert mail.data["username"] == test_user.get("username")
    assert mail.template == "reset_password.html"

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset requested successfully"


def test_request_password_reset_on_unregistered_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "api/auth/request_password_reset",
        json={"email": "unregistered_user@example.com"},
    )

    mock_send_email.assert_not_called()

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset requested successfully"


@pytest.mark.asyncio
async def test_password_reset(client):
    password_reset_token = await auth_service.create_password_reset_token(
        User(email=test_user.get("email"))
    )
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.password_reset_token = password_reset_token
            await session.commit()

    response = client.post(
        "api/auth/password_reset",
        json={
            "password": "new_user_password",
            "password_reset_token": password_reset_token,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password updated successfully"

    async with TestingSessionLocal() as session:
        user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        user = user.scalar_one_or_none()
        if user:
            assert password_hasher.verify_password("new_user_password", user.password)
            assert user.password_reset_token is None


def test_password_reset_on_invalid_token(client):
    response = client.post(
        "api/auth/password_reset",
        json={
            "password": "new_user_password",
            "password_reset_token": "invalid_token",
        },
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Token is invalid"


@pytest.mark.asyncio
async def test_password_reset_form(client):
    password_reset_token = await auth_service.create_password_reset_token(
        User(email=test_user.get("email"))
    )
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.password_reset_token = password_reset_token
            await session.commit()

    response = client.get(
        f"api/auth/password_reset/{password_reset_token}",
    )
    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"

    async with TestingSessionLocal() as session:
        user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        user = user.scalar_one_or_none()
        if user:
            assert user.password_reset_token is not None


def test_password_reset_form_on_invalid_token(client):
    response = client.get(
        "api/auth/password_reset/invalid_token",
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Token is invalid"
