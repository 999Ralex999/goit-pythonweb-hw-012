from datetime import datetime
from typing import Any
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.contact import ContactModel, ContactQuery
from app.entity.bootstrap import Contact
from app.repository.contact import ContactRepository


def get_birthday_in_next_days_query(birthday_in_next_days: int) -> tuple[int, int]:
    today = datetime.now().timetuple().tm_yday
    if today + birthday_in_next_days > 365:
        to_day = today + birthday_in_next_days - 365
    else:
        to_day = today + birthday_in_next_days

    return (today, to_day)


query_cases = [
    pytest.param(
        ContactQuery(),
        ["LIMIT :param_1", "OFFSET :param_2"],
        {"param_1": 10, "param_2": 0},
        id="empty query",
    ),
    pytest.param(
        ContactQuery(limit=100, offset=10),
        ["LIMIT :param_1", "OFFSET :param_2"],
        {"param_1": 100, "param_2": 10},
        id="limit and offset query",
    ),
    pytest.param(
        ContactQuery(search="John"),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "lower(contacts.first_name) LIKE",
            "lower(contacts.last_name) LIKE",
            "lower(contacts.email) LIKE",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "first_name_1": "%John%",
            "last_name_1": "%John%",
            "email_1": "%John%",
        },
        id="search query",
    ),
    pytest.param(
        ContactQuery(first_name="John"),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.first_name =",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "first_name_1": "John",
        },
        id="first_name query",
    ),
    pytest.param(
        ContactQuery(last_name="John"),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.last_name =",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "last_name_1": "John",
        },
        id="last_name query",
    ),
    pytest.param(
        ContactQuery(email="john.doe@example.com"),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.email =",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "email_1": "john.doe@example.com",
        },
        id="email query",
    ),
    pytest.param(
        ContactQuery(phone="1234567890"),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.phone =",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "phone_1": "1234567890",
        },
        id="phone query",
    ),
    pytest.param(
        ContactQuery(birthday_from=datetime(1990, 1, 1)),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday >=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_1": datetime(1990, 1, 1),
        },
        id="birthday from query",
    ),
    pytest.param(
        ContactQuery(birthday_to=datetime(1990, 1, 1)),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday <=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_1": datetime(1990, 1, 1),
        },
        id="birthday to query",
    ),
    pytest.param(
        ContactQuery(birthday_of_the_year_from=8),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday_of_the_year >=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_of_the_year_1": 8,
        },
        id="birthday of the year from query",
    ),
    pytest.param(
        ContactQuery(birthday_of_the_year_to=8),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday_of_the_year <=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_of_the_year_1": 8,
        },
        id="birthday of the year to query",
    ),
    pytest.param(
        ContactQuery(birthday_in_next_days=9),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday_of_the_year <=",
            "contacts.birthday_of_the_year >=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_of_the_year_1": get_birthday_in_next_days_query(9)[0],
            "birthday_of_the_year_2": get_birthday_in_next_days_query(9)[1],
        },
        id="birthday in next days query",
    ),
    pytest.param(
        ContactQuery(
            birthday_in_next_days=(365 - datetime.now().timetuple().tm_yday) + 8
        ),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday_of_the_year <=",
            "contacts.birthday_of_the_year >=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_of_the_year_1": get_birthday_in_next_days_query(
                (365 - datetime.now().timetuple().tm_yday) + 8
            )[0],
            "birthday_of_the_year_2": get_birthday_in_next_days_query(
                (365 - datetime.now().timetuple().tm_yday) + 8
            )[1],
        },
        id="birthday in next days query next year",
    ),
    pytest.param(
        ContactQuery(birthday_of_the_year_to=8, birthday_of_the_year_from=8),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.birthday_of_the_year <=",
            "contacts.birthday_of_the_year >=",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "birthday_of_the_year_1": 8,
            "birthday_of_the_year_2": 8,
        },
        id="combined query",
    ),
    pytest.param(
        ContactQuery(
            phone="1234567890",
            first_name="John",
            last_name="Doe",
        ),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.phone =",
            "contacts.first_name =",
            "contacts.last_name =",
        ],
        {
            "param_1": 10,
            "param_2": 0,
            "phone_1": "1234567890",
            "first_name_1": "John",
            "last_name_1": "Doe",
        },
        id="combined query by phone, first name and last name",
    ),
    pytest.param(
        ContactQuery(
            phone="1234567890",
            email="john.doe@example.com",
            limit=100,
            offset=10,
        ),
        [
            "LIMIT :param_1",
            "OFFSET :param_2",
            "contacts.phone =",
            "contacts.email =",
        ],
        {
            "param_1": 100,
            "param_2": 10,
            "phone_1": "1234567890",
            "email_1": "john.doe@example.com",
        },
        id="combined query by phone, email wiht limit and offset",
    ),
]


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def contact():
    return Contact(
        id=1,
        user_id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthday=datetime(1990, 1, 1),
        additional_info="Additional info",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(None, id="Without user id"),
        pytest.param(1, id="With user id"),
    ],
)
async def test_get_by_id(contact_repository, mock_session, contact, user_id):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    if user_id is None:
        contact = await contact_repository.get_by_id(1)
    else:
        contact = await contact_repository.get_by_id(1, user_id)

    call_args = mock_session.execute.call_args[0][0].compile()
    sql_str = str(call_args)
    params = call_args.params

    mock_session.execute.assert_called_once()

    assert contact is not None
    assert contact.id == 1
    assert contact.user_id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == datetime(1990, 1, 1)
    assert contact.additional_info == "Additional info"
    assert "SELECT" in sql_str
    assert "contacts" in sql_str
    assert "contacts.id = " in sql_str
    assert "id_1" in params
    assert params["id_1"] == 1
    if user_id is None:
        assert "contacts.user_id =" not in sql_str
        assert len(params.keys()) == 1
    else:
        assert "contacts.user_id =" in sql_str
        assert len(params.keys()) == 2
        assert "user_id_1" in params
        assert params["user_id_1"] == user_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(contact_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_by_id(2)

    assert contact is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(None, id="Without user id"),
        pytest.param(1, id="With user id"),
    ],
)
async def test_get_by_email(contact_repository, mock_session, contact, user_id):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    if user_id is None:
        contact = await contact_repository.get_by_email("john.doe@example.com")
    else:
        contact = await contact_repository.get_by_email("john.doe@example.com", user_id)

    compiled = mock_session.execute.call_args[0][0].compile()
    sql_str = str(compiled)
    params = compiled.params

    mock_session.execute.assert_called_once()

    assert contact is not None
    assert contact.id == 1
    assert contact.user_id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == datetime(1990, 1, 1)
    assert contact.additional_info == "Additional info"
    assert "SELECT" in sql_str
    assert "contacts" in sql_str
    assert "contacts.email = " in sql_str
    assert "contacts.id =" not in sql_str
    assert params["email_1"] == "john.doe@example.com"

    if user_id is None:
        assert "contacts.user_id =" not in sql_str
        assert len(params.keys()) == 1
    else:
        assert "contacts.user_id =" in sql_str
        assert len(params.keys()) == 2
        assert "user_id_1" in params
        assert params["user_id_1"] == user_id


@pytest.mark.asyncio
async def test_get_by_email_not_found(contact_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_by_email("john.doe@example.com2")

    assert contact is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, constraints, query_params",
    query_cases,
)
async def test_query_without_user_id(
    contact_repository,
    mock_session,
    contact,
    query: ContactQuery,
    constraints: list[str],
    query_params: dict[str, Any],
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    resutlt = await contact_repository.query(query)
    compiled = mock_session.execute.call_args[0][0].compile()
    sql_str = str(compiled)
    params = compiled.params

    mock_session.execute.assert_called_once()

    assert resutlt is not None
    assert len(resutlt) == 1
    assert resutlt[0] is not None
    assert isinstance(resutlt[0], Contact)
    assert resutlt[0].id == 1
    assert resutlt[0].user_id == 1
    assert resutlt[0].first_name == "John"
    assert resutlt[0].last_name == "Doe"
    assert resutlt[0].email == "john.doe@example.com"
    assert resutlt[0].phone == "1234567890"
    assert "SELECT" in sql_str
    assert "contacts" in sql_str
    assert "contacts.user_id =" not in sql_str

    for constraint in constraints:
        assert constraint in sql_str

    for key, value in query_params.items():
        assert key in params
        assert params[key] == value

    assert len(params.keys()) == len(query_params.keys())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, constraints, query_params",
    query_cases,
)
async def test_query_with_user_id(
    contact_repository,
    mock_session,
    contact,
    query: ContactQuery,
    constraints: list[str],
    query_params: dict[str, Any],
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    resutlt = await contact_repository.query(query, 1)
    compiled = mock_session.execute.call_args[0][0].compile()
    sql_str = str(compiled)
    params = compiled.params

    mock_session.execute.assert_called_once()

    query_params["user_id_1"] = 1

    assert resutlt is not None
    assert len(resutlt) == 1
    assert resutlt[0] is not None
    assert isinstance(resutlt[0], Contact)
    assert resutlt[0].id == 1
    assert resutlt[0].user_id == 1
    assert resutlt[0].first_name == "John"
    assert resutlt[0].last_name == "Doe"
    assert resutlt[0].email == "john.doe@example.com"
    assert resutlt[0].phone == "1234567890"
    assert "SELECT" in sql_str
    assert "contacts" in sql_str
    assert "contacts.user_id =" in sql_str

    for constraint in constraints:
        assert constraint in sql_str

    for key, value in query_params.items():
        assert key in params
        assert params[key] == value

    assert len(params.keys()) == len(query_params.keys())


@pytest.mark.asyncio
async def test_query_with_user_id_empty_result(
    contact_repository,
    mock_session,
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    resutlt = await contact_repository.query(ContactQuery(), 1)

    mock_session.execute.assert_called_once()

    assert resutlt is not None
    assert len(resutlt) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(None, id="Without user id"),
        pytest.param(1, id="With user id"),
    ],
)
async def test_update(contact_repository, mock_session, contact, user_id):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    model = ContactModel(
        first_name="new first name",
        last_name="new last name",
    )

    if user_id is None:
        contact = await contact_repository.update(1, model)
    else:
        contact = await contact_repository.update(1, model, user_id)

    call_args = mock_session.execute.call_args[0][0].compile()
    sql_str = str(call_args)
    params = call_args.params

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)
    mock_session.execute.assert_called_once()

    assert isinstance(contact, Contact)
    assert contact.id == 1
    assert contact.user_id == 1
    assert contact.first_name == "new first name"
    assert contact.last_name == "new last name"
    assert contact.email == "john.doe@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == datetime(1990, 1, 1)
    assert contact.additional_info == "Additional info"
    assert "SELECT" in sql_str
    assert "contacts" in sql_str
    assert "contacts.id = " in sql_str
    assert "id_1" in params
    assert params["id_1"] == 1
    if user_id is None:
        assert "contacts.user_id =" not in sql_str
        assert len(params.keys()) == 1
    else:
        assert "contacts.user_id =" in sql_str
        assert len(params.keys()) == 2
        assert "user_id_1" in params
        assert params["user_id_1"] == user_id


@pytest.mark.asyncio
async def test_update_not_found(contact_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    model = ContactModel(
        first_name="new first name",
        last_name="new last name",
    )

    contact = await contact_repository.update(1, model, 1)
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()
    mock_session.execute.assert_called_once()

    assert contact is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(None, id="Without user id"),
        pytest.param(1, id="With user id"),
    ],
)
async def test_delete(contact_repository, mock_session, contact, user_id):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    if user_id is None:
        await contact_repository.delete(1)
    else:
        await contact_repository.delete(1, user_id)

    call_args = mock_session.execute.call_args[0][0].compile()
    sql_str = str(call_args)
    params = call_args.params

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_called_once_with(contact)
    mock_session.commit.assert_awaited_once()

    assert "SELECT" in sql_str
    assert "contacts" in sql_str
    assert "contacts.id = " in sql_str
    assert "id_1" in params
    assert params["id_1"] == 1
    if user_id is None:
        assert "contacts.user_id =" not in sql_str
        assert len(params.keys()) == 1
    else:
        assert "contacts.user_id =" in sql_str
        assert len(params.keys()) == 2
        assert "user_id_1" in params
        assert params["user_id_1"] == user_id


@pytest.mark.asyncio
async def test_delete_not_found(contact_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    await contact_repository.delete(2, 1)

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(None, id="Without user id"),
        pytest.param(1, id="With user id"),
    ],
)
async def test_create(contact_repository, mock_session, user_id):

    model = ContactModel(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthday=datetime(1990, 1, 1),
        additional_info="Additional info",
    )

    async def add_contact_id(contact_obj):
        contact_obj.id = 1

    mock_session.refresh = AsyncMock(side_effect=add_contact_id)

    if user_id is None:
        contact = await contact_repository.create(model)
    else:
        contact = await contact_repository.create(model, user_id)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)

    assert isinstance(contact, Contact)
    assert contact.id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == datetime(1990, 1, 1)
    assert contact.additional_info == "Additional info"
    assert contact.user_id == user_id
