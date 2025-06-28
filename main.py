from fastapi import HTTPException
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from app.exceptions.token_decode_exception import TokenDecodeException
from app.conf.config import settings
from app.middlewares.logger import add_process_time_header
from app.api.utils import router as utils_router
from app.api.contacts import router as contacts_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI()

app.include_router(utils_router, prefix="/api")
app.include_router(contacts_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")

app.middleware("http")(add_process_time_header)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DOMAIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
    """
    Handle HTTP exception

    Args:
        request (Request): The request that caused the HTTP exception
        exc (HTTPException): The exception that was raised

    Returns:
        JSONResponse: The response to the request
    """
    return JSONResponse(
        status_code=exc.status_code, content={"detail": str(exc.detail)}
    )


@app.exception_handler(TokenDecodeException)
def handle_token_decode_exception(request: Request, exc: TokenDecodeException):
    """
    Handle token decode exception

    Args:
        request (Request): The request that caused the token decode exception
        exc (TokenDecodeException): The exception that was raised

    Returns:
        JSONResponse: The response to the request
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc.message)}
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle rate limit exceeded exception

    Args:
        request (Request): The request that caused the rate limit to be exceeded
        exc (RateLimitExceeded): The exception that was raised

    Returns:
        JSONResponse: The response to the request
    """
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"},
    )


if __name__ == "__main__":
    print("To start the server, run: uvicorn main:app --reload")
