from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.admin import setup_admin
from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.session import SessionLocal, engine
from app.scripts.create_admin import ensure_startup_admin_user

settings = get_settings()
cors_allow_origins = [
    origin.strip()
    for origin in settings.cors_allow_origins.split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await ensure_startup_admin_user(
        session_maker=SessionLocal,
        settings=settings,
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Study CRM Python Backend",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    setup_admin(
        app,
        session_maker=SessionLocal,
        admin_engine=engine,
        settings=settings,
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
