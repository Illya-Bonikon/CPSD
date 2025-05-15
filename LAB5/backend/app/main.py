from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .db.mongodb import mongodb
from .core.config import get_settings
from .api.v1.api import api_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=settings.API_OPENAPI_URL,
    docs_url=settings.API_DOCS_URL,
    redoc_url=settings.API_REDOC_URL,
)

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обробка помилок
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутрішня помилка сервера"},
    )

# Події життєвого циклу
@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.close_mongodb_connection()

# Включаємо роутери API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Тестовий ендпоінт
@app.get("/")
async def root():
    """
    Кореневий ендпоінт для перевірки роботи API.
    """
    return {
        "message": "Genetic Algorithm API",
        "docs_url": settings.API_DOCS_URL,
        "redoc_url": settings.API_REDOC_URL
    } 