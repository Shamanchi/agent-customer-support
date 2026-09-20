"""
FastAPI application factory and main entrypoint for Agent Customer Support.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import tickets, classify, generate, escalate, webhooks
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import close_db, init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Agent Customer Support...")
    configure_logging()
    await init_db()

    # Create Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    logger.info("Application started")
    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Application stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Agent Customer Support",
        description="AI-powered customer support agent with ticket classification, response generation, and escalation",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(tickets.router, prefix="/api/v1")
    app.include_router(classify.router, prefix="/api/v1")
    app.include_router(generate.router, prefix="/api/v1")
    app.include_router(escalate.router, prefix="/api/v1")
    app.include_router(webhooks.router, prefix="/api/v1")

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": "Agent Customer Support",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )