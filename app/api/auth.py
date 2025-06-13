from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas.user import (
    UserCreateRequest,
    UserModel,
    UserResendVerificationEmailRequest,
    UserResponse,
)
from app.schemas.auth import AuthResponse, TokenRefreshRequest
from app.db.session import get_db
from app.services.user import UserService
from app.services.auth import auth_service, get_current_user
from app.repository.contact import ContactRepository
from app.models.user import User
from app.exceptions.user_exists_exception import UserExistsException

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    user_request: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)

    try:
        user = await service.create_user(
            UserModel(
                username=user_request.username,
                email=user_request.email,
                password=user_request.password,
            )
        )
    except UserExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    return user

@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    oauth2_request: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository)
    user = await service.get_user_by_username(oauth2_request.username)

    if not user or not await auth_service.verify_password(oauth2_request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")

    refresh_token = await auth_service.create_refresh_token(user)
    await service.update_refresh_token(user, refresh_token)

    return AuthResponse(
        access_token=await auth_service.create_access_token(user),
        refresh_token=refresh_token,
    )

@router.post("/refresh_token", response_model=AuthResponse)
async def refresh_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.verify_refresh_token(request.refresh_token, db)
    return AuthResponse(
        access_token=await auth_service.create_access_token(user),
        refresh_token=request.refresh_token,
    )

@router.get("/confirmed_email/{token}")
async def confirmed_email(
    background_tasks: BackgroundTasks,
    token: str = Path(..., description="The verification token"),
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)
    await service.confirm_email(token)
    return {"message": "Email confirmed"}

@router.post("/resend_verification_email")
@limiter.limit("2/minute")
async def resend_verification_email(
    request: Request,
    background_tasks: BackgroundTasks,
    user_request: UserResendVerificationEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)
    user = await service.get_user_by_email(user_request.email)

    if user and user.email_verified:
        return {"message": "Email already verified"}

    if user:
        await service.send_verification_email(user)

    return {"message": "Verification email sent"}

@router.get("/me", response_model=UserResponse)
@limiter.limit("3/minute")
async def get_me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user
