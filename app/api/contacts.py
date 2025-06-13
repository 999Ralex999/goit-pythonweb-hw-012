from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.contact import ContactModel, ContactQuery, ContactResponse
from app.db.session import get_db
from app.services.contact import ContactService
from app.repositories.contact import ContactRepository
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    query: ContactQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    service = ContactService(repo)
    return await service.query(query, current_user.id)

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactModel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    service = ContactService(repo)
    return await service.create(contact, current_user.id)

@router.get("/closest-birthday", response_model=List[ContactResponse])
async def closest_birthdays(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    service = ContactService(repo)
    return await service.get_closest_birthday(7, limit, offset, current_user.id)

@router.get("/{id}", response_model=ContactResponse)
async def get_contact(
    id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    service = ContactService(repo)
    contact = await service.get_by_id(id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{id}", response_model=ContactResponse)
async def update_contact(
    contact_model: ContactModel,
    id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    service = ContactService(repo)
    contact = await service.update(id, contact_model, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    service = ContactService(repo)
    await service.delete(id, current_user.id)

