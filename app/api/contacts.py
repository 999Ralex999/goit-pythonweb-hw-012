from typing import List
from fastapi import APIRouter, Body, HTTPException, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.user import User
from app.database.db import get_db
from app.repository.contact import ContactRepository
from app.schemas.contact import (
    ContactCreateRequest,
    ContactModel,
    ContactQuery,
    ContactResponse,
)
from app.services.contact import ContactService
from app.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponse],
    status_code=status.HTTP_200_OK,
    description="Get all contacts",
)
async def contacts(
    query: ContactQuery = Query(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_repository = ContactRepository(db)
    contact_service = ContactService(contact_repository)
    contacts = await contact_service.query(query, current_user.id)
    return contacts


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new contact",
)
async def create_contact(
    contact_request: ContactCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_repository = ContactRepository(db)
    contact_service = ContactService(contact_repository)
    try:
        contact = await contact_service.create(
            ContactModel(
                **contact_request.model_dump(),
            ),
            current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return contact


@router.get(
    "/closest-birthday",
    response_model=List[ContactResponse],
    status_code=status.HTTP_200_OK,
    description="Get contacts with closest birthday in the next 7 days",
)
async def contacts_closest_birthday(
    limit: int = Query(
        default=10, ge=1, le=100, description="Limit the number of contacts to return"
    ),
    offset: int = Query(
        default=0, ge=0, description="Offset the number of contacts to return"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_repository = ContactRepository(db)
    contact_service = ContactService(contact_repository)
    contacts = await contact_service.get_closest_birthday(
        7, limit, offset, current_user.id
    )
    return contacts


@router.put(
    "/{id}",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    description="Update a contact",
)
async def update_contact(
    contact_model: ContactModel,
    id: int = Path(ge=1, description="The ID of the contact"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_repository = ContactRepository(db)
    contact_service = ContactService(contact_repository)
    contact = await contact_service.update(id, contact_model, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.get(
    "/{id}",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    description="Get a contact by ID",
)
async def get_contact(
    id: int = Path(ge=1, description="The ID of the contact"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_repository = ContactRepository(db)
    contact_service = ContactService(contact_repository)
    contact = await contact_service.get_by_id(id, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a contact",
)
async def delete_contact(
    id: int = Path(ge=1, description="The ID of the contact"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_repository = ContactRepository(db)
    contact_service = ContactService(contact_repository)
    await contact_service.delete(id, current_user.id)
