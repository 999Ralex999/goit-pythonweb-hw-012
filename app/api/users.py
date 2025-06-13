from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.repository.contact import ContactRepository
from app.services.user import UserService
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.patch("/avatar", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_avatar(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="User avatar"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    service = UserService(repo, background_tasks)
    return await service.update_avatar(current_user, file)
