from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
    BackgroundTasks,
)
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.base import MessageResponse
from app.exceptions.token_decode_exception import TokenDecodeException
from app.exceptions.user_exists_exception import UserExistsException
from app.schemas.auth import AuthResponse, TokenRefreshRequest
from app.entity.user import User
from app.services.user import UserService
from app.repository.user import UserRepository
from app.database.db import get_db
from app.schemas.user import (
    UserCreateRequest,
    UserModel,
    UserPasswordRestoreRequest,
    UserPasswordUpdateRequest,
    UserResendVerificationEmailRequest,
    UserResponse,
)
from app.services.auth import auth_service, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Register a new user",
)
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
                role=user_request.role,
            )
        )
    except UserExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return user


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="Get current user",
)
@limiter.limit("3/minute")
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    description="Login a user",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    oauth2_request: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository)

    user = await service.get_user_by_username(oauth2_request.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not await auth_service.verify_password(oauth2_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
        )

    refresh_token = await auth_service.create_refresh_token(user)

    await service.update_refresh_token(user, refresh_token)

    return AuthResponse(
        access_token=await auth_service.create_access_token(user),
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh_token",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    description="Refresh a token",
)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.verify_refresh_token(request.refresh_token, db)
    return AuthResponse(
        access_token=await auth_service.create_access_token(user),
        refresh_token=request.refresh_token,
    )


@router.get(
    "/confirmed_email/{token}",
    status_code=status.HTTP_200_OK,
    description="Confirm a user's email",
)
async def confirmed_email(
    background_tasks: BackgroundTasks,
    token: str = Path(description="The token of the user"),
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)

    try:
        await service.confirm_email(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageResponse(message="Email confirmed")


@router.post(
    "/resend_verification_email",
    status_code=status.HTTP_200_OK,
    description="Resend a verification email",
)
@limiter.limit("3/minute")
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

    if user and not user.email_verified:
        await service.send_verification_email(user)

    return MessageResponse(message="Verification email sent")


@router.post(
    "/request_password_reset",
    status_code=status.HTTP_200_OK,
    description="Request a password reset",
)
@limiter.limit("2/minute")
async def request_password_reset(
    request: Request,
    background_tasks: BackgroundTasks,
    user_request: UserPasswordRestoreRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)

    await service.request_password_reset(user_request.email)

    return MessageResponse(message="Password reset requested successfully")


@router.post(
    "/password_reset",
    status_code=status.HTTP_200_OK,
    description="Change a user's password",
)
@limiter.limit("2/minute")
async def password_reset(
    request: Request,
    background_tasks: BackgroundTasks,
    user_request: UserPasswordUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repository = UserRepository(db)
    service = UserService(user_repository, background_tasks)

    user = await auth_service.verify_password_reset_token(
        user_request.password_reset_token, db
    )

    await service.reset_password(user, user_request.password)

    return MessageResponse(message="Password updated successfully")


@router.get(
    "/password_reset/{token}",
    status_code=status.HTTP_200_OK,
    description="Reset a user's password",
)
async def reset_password(
    request: Request,
    token: str = Path(description="The token of the user"),
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.verify_password_reset_token(token, db)

    return Jinja2Templates(directory="templates").TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "token": token,
            "username": user.username,
        },
    )
