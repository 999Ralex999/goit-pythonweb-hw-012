from unittest.mock import Mock
import pytest


def test_signup_with_empty_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    user_data = {
        "username": "user_empty_email",
        "email": "",
        "password": "validpass123",
        "role": "USER",
    }

    response = client.post("api/auth/register", json=user_data)
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data
    assert any(
        violation["loc"] == ["body", "email"]
        and violation["msg"].startswith("value is not a valid email address")
        for violation in data["detail"]
    )


def test_resend_verification_email_empty(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "api/auth/resend_verification_email",
        json={"email": ""},
    )
    data = response.json()

    assert response.status_code == 422
    assert "detail" in data
    assert any(
        violation["loc"] == ["body", "email"]
        and violation["msg"].startswith("value is not a valid email address")
        for violation in data["detail"]
    )


def test_login_with_empty_fields(client):
    response = client.post(
        "api/auth/login",
        data={"username": "", "password": ""},
    )
    data = response.json()

    assert response.status_code == 401
    assert "detail" in data


def test_request_password_reset_empty_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.mail_service.send_email", mock_send_email)

    response = client.post(
        "/api/auth/request_password_reset",
        json={"email": ""},
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_register_with_weak_password(client):
    data = {"username": "weakpass", "email": "weak@example.com", "password": "123"}
    response = client.post("api/auth/register", json=data)
    assert response.status_code == 422  


def test_resend_verification_with_invalid_email(client):
    response = client.post("api/auth/verify", json={"email": "not-an-email"})
    assert response.status_code == 404



def test_request_password_reset_for_invalid_email_format(client):
    response = client.post("api/auth/request-password-reset", json={"email": "invalid-format"})
    assert response.status_code == 404


def test_request_password_reset_for_unregistered_email(client):
    response = client.post("api/auth/request-password-reset", json={"email": "unreg@example.com"})
    assert response.status_code == 404

    
