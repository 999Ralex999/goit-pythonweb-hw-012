import pytest
from tests.integration.conftest import test_contacts

violation_cases = [
    pytest.param(
        {
            "first_name": "John",
            "last_name": "Doe",
        },
        [
            {
                "type": "missing",
                "loc": ["body", "email"],
                "msg": "Field required",
                "input": {
                    "first_name": "John",
                    "last_name": "Doe",
                },
            }
        ],
        id="Create contact without email",
    ),
    pytest.param(
        {
            "first_name": "",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        },
        [
            {
                "type": "string_too_short",
                "loc": ["body", "first_name"],
                "msg": "String should have at least 1 character",
                "input": "",
                "ctx": {"min_length": 1},
            }
        ],
        id="Create contact with empty first_name",
    ),
    pytest.param(
        {
            "first_name": "",
            "last_name": "",
            "email": "john.doe@example.com",
        },
        [
            {
                "type": "string_too_short",
                "loc": ["body", "first_name"],
                "msg": "String should have at least 1 character",
                "input": "",
                "ctx": {"min_length": 1},
            },
            {
                "type": "string_too_short",
                "loc": ["body", "last_name"],
                "msg": "String should have at least 1 character",
                "input": "",
                "ctx": {"min_length": 1},
            },
        ],
        id="Create contact with empty first_name and last_name",
    ),
    pytest.param(
        {
            "first_name": "Name",
            "email": "john.doe-example.com",
        },
        [
            {
                "type": "value_error",
                "loc": ["body", "email"],
                "msg": "value is not a valid email address: An email address must have an @-sign.",
                "input": "john.doe-example.com",
                "ctx": {"reason": "An email address must have an @-sign."},
            },
        ],
        id="Create contact with invalid email",
    ),
]


@pytest.mark.parametrize(
    "contact_data,",
    [
        pytest.param(
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe1@example.com",
                "phone": "+1234567890",
                "birthday": "2025-06-21T00:00:00",
                "additional_info": "Additional info",
            },
            id="Create contact with all fields",
        ),
        pytest.param(
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe1@example.com",
            },
            id="Create contact with first_name, last_name and email",
        ),
        pytest.param(
            {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567891",
                "email": "john.doe1@example.com",
            },
            id="Create contact with first_name, last_name and phone",
        ),
    ],
)
def test_create_contact_success(client, get_token, contact_data):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("api/contacts", headers=headers, json=contact_data)
    assert response.status_code == 201, response.text
    data = response.json()
    for key, value in contact_data.items():
        assert data[key] == value


def test_create_contact_email_duplicate(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    client.post(
        "api/contacts",
        headers=headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        },
    )
    response = client.post(
        "api/contacts",
        headers=headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        },
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Contact with this email already exists"


def test_create_contact_unauthorized(client):
    response = client.post(
        "api/contacts",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "contact_data, response_data",
    violation_cases,
)
def test_create_contact_invalid_data(client, get_token, contact_data, response_data):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post(
        "api/contacts",
        headers=headers,
        json=contact_data,
    )
    data = response.json()
    assert response.status_code == 422, response.text
    assert "detail" in data

    detail = data["detail"]
    assert len(detail) == len(response_data)

    for i, violation in enumerate(response_data):
        for key, expected_value in violation.items():
            assert (
                detail[i][key] == expected_value
            ), f"Mismatch in violation {i}, key {key}"


def test_get_contacts_empty(client, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    response = client.get("api/contacts", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 0


def test_get_contacts_unauthorized(client):
    response = client.get("api/contacts")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "query, response_data",
    [
        pytest.param(
            {},
            test_contacts,
            id="Get all contacts",
        ),
        pytest.param(
            {"limit": 1},
            test_contacts[:1],
            id="Get all contacts with limit 1",
        ),
        pytest.param(
            {"limit": 1, "offset": 1},
            test_contacts[1:2],
            id="Get all contacts with limit 1 and offset 1",
        ),
        pytest.param(
            {"first_name": "John"},
            [test_contacts[0]],
            id="Get all contacts with first_name query",
        ),
        pytest.param(
            {"first_name": "John", "last_name": "Doe"},
            [test_contacts[0]],
            id="Get all contacts with first_name and last_name query",
        ),
        pytest.param(
            {"email": "jane.smith@example.com"},
            [test_contacts[1]],
            id="Get all contacts with email query",
        ),
        pytest.param(
            {"phone": "+1234567891"},
            [test_contacts[1]],
            id="Get all contacts with phone query",
        ),
        pytest.param(
            {"birthday_from": "1992-02-01", "birthday_to": "1992-03-04"},
            [test_contacts[2]],
            id="Get all contacts with birthday from and to query",
        ),
        pytest.param(
            {"birthday_of_the_year_from": 1, "birthday_of_the_year_to": 365},
            test_contacts,
            id="Get all contacts with birthday_of_the_year from and to query",
        ),
        pytest.param(
            {"birthday_of_the_year_from": 1, "birthday_of_the_year_to": 3},
            [test_contacts[0]],
            id="Get all contacts with birthday_of_the_year from and to query",
        ),
    ],
)
def test_get_contacts(client, get_token, query, response_data):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("api/contacts", headers=headers, params=query)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == len(response_data)
    for i, contact in enumerate(response_data):
        assert data[i]["first_name"] == contact["first_name"]
        assert data[i]["last_name"] == contact["last_name"]
        assert data[i]["email"] == contact["email"]
        assert data[i]["phone"] == contact["phone"]
        assert data[i]["birthday"] == contact["birthday"].isoformat()
        assert data[i]["additional_info"] == contact["additional_info"]


def test_get_closest_birthday(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("api/contacts/closest-birthday", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == test_contacts[3]["first_name"]
    assert data[0]["last_name"] == test_contacts[3]["last_name"]
    assert data[0]["email"] == test_contacts[3]["email"]
    assert data[0]["phone"] == test_contacts[3]["phone"]
    assert data[0]["birthday"] == test_contacts[3]["birthday"].isoformat()


def test_get_closest_birthday_unauthorized(client):
    response = client.get("api/contacts/closest-birthday")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "contact_data, response_data",
    [
        pytest.param(
            {
                "first_name": "John_new",
                "last_name": "Doe_new",
                "email": "john.doe_new@example.com",
                "phone": "+1234567892",
                "birthday": "2025-06-21T00:00:00",
                "additional_info": "Additional info_new",
            },
            {
                "first_name": "John_new",
                "last_name": "Doe_new",
                "email": "john.doe_new@example.com",
                "phone": "+1234567892",
                "birthday": "2025-06-21T00:00:00",
                "additional_info": "Additional info_new",
            },
            id="Update contact with all fields",
        ),
        pytest.param(
            {
                "first_name": "John_new",
                "last_name": "Doe_new",
            },
            {
                "first_name": "John_new",
                "last_name": "Doe_new",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "birthday": "1990-01-01T00:00:00",
                "additional_info": "Test contact 1",
            },
            id="Update contact with first_name and last_name",
        ),
        pytest.param(
            {
                "phone": "+1234567891",
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567891",
                "birthday": "1990-01-01T00:00:00",
                "additional_info": "Test contact 1",
            },
            id="Update contact with phone",
        ),
    ],
)
def test_update_contact_success(client, get_token, contact_data, response_data):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.put(
        "api/contacts/1",
        headers=headers,
        json=contact_data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    for key, value in response_data.items():
        assert data[key] == value


def test_update_contact_not_found(client, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    response = client.put("api/contacts/100", headers=headers, json={})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact_unauthorized(client):
    response = client.put("api/contacts/1", json={})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "id, contact_data",
    [
        pytest.param(1, test_contacts[0], id="Get contact with id 1"),
        pytest.param(2, test_contacts[1], id="Get contact with id 2"),
        pytest.param(3, test_contacts[2], id="Get contact with id 3"),
        pytest.param(4, test_contacts[3], id="Get contact with id 4"),
    ],
)
def test_get_contact_success(client, get_token, id, contact_data):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get(f"api/contacts/{id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == id
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]
    assert data["birthday"] == contact_data["birthday"].isoformat()
    assert data["additional_info"] == contact_data["additional_info"]


def test_get_contact_not_found(client, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    response = client.get("api/contacts/1", headers=headers)
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contact_unauthorized(client):
    response = client.get("api/contacts/1")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_delete_contact_success(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.delete("api/contacts/1", headers=headers)
    assert response.status_code == 204, response.text
    response = client.get("api/contacts/1", headers=headers)
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact_unauthorized(client):
    response = client.delete("api/contacts/1")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"
