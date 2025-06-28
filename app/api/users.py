from typing import List
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.user import User
from app.repository.user import UserRepository
from app.schemas.user import UserResponse
from app.database.db import get_db
from app.services.user import UserService
from app.services.auth import get_current_admin_user


router = APIRouter(prefix="/users", tags=["users"])


@router.patch(
    "/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="Update avatar",
)
async def update_avatar(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(description="The avatar file"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)
    return await service.update_avatar(current_user, file)
