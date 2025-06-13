from fastapi import HTTPException, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.middlewares.logger import add_process_time_header

from app.api.utils import router as utils_router
from app.api.contacts import router as contacts_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI()

# Підключаємо маршрути (роутери)
app.include_router(utils_router, prefix="/api")
app.include_router(contacts_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")

# Підключаємо кастомний мідлвар для логування запитів
app.middleware("http")(add_process_time_header)

# Налаштовуємо CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DOMAIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обробник HTTP-винятків FastAPI
@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

# Обробник RateLimitExceeded (slowapi)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"},
    )

if __name__ == "__main__":
    print("To start the server, run: uvicorn main:app --reload")


