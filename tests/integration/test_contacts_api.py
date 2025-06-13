import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from datetime import datetime

@pytest.mark.asyncio
async def test_crud_contacts():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True
    ) as client:
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "123456789",
            "birthday": datetime.now().isoformat(),
            "additional_info": "Test contact"
        }

        # CREATE
        response = await client.post("/api/contacts", json=payload)
        assert response.status_code == 200
        contact_id = response.json()["id"]

        # GET ALL
        response = await client.get("/api/contacts")
        assert response.status_code == 200
        assert any(c["id"] == contact_id for c in response.json())

        # GET ONE
        response = await client.get(f"/api/contacts/{contact_id}")
        assert response.status_code == 200
        assert response.json()["id"] == contact_id

        # UPDATE
        updated_payload = payload.copy()
        updated_payload["first_name"] = "Jane"
        response = await client.put(f"/api/contacts/{contact_id}", json=updated_payload)
        assert response.status_code == 200
        assert response.json()["first_name"] == "Jane"

        # DELETE
        response = await client.delete(f"/api/contacts/{contact_id}")
        assert response.status_code == 200
