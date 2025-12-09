"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")


# Development only endpoints
if settings.debug:
    @app.get("/")
    async def root():
        """Root endpoint (development only)."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "environment": "development",
        }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
