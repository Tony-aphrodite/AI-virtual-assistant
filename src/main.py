"""
FastAPI application entry point for AI Virtual Assistant.

This is the main application file that sets up:
- FastAPI app with middleware
- API routes and webhooks
- CORS configuration
- Lifespan events (startup/shutdown)
- Error handlers
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.core.exceptions import AIAssistantException
from src.core.logging import get_logger, setup_logging
from src.db.session import check_db_connection, close_db_connections

# Set up logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting AI Virtual Assistant",
        version="0.1.0",
        environment=settings.environment,
    )

    # Check database connection
    db_healthy = await check_db_connection()
    if not db_healthy:
        logger.error("Database connection failed on startup")
    else:
        logger.info("Database connection established")

    yield

    # Shutdown
    logger.info("Shutting down AI Virtual Assistant")
    await close_db_connections()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Enterprise-grade AI Virtual Assistant with phone, email, and WhatsApp integration",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,  # Disable docs in production
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Exception handlers
@app.exception_handler(AIAssistantException)
async def ai_assistant_exception_handler(
    request: Request, exc: AIAssistantException
) -> JSONResponse:
    """Handle custom AI Assistant exceptions."""
    logger.error(
        "AI Assistant error",
        error_code=exc.code,
        error_message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    logger.error(
        "Unhandled exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        exc_info=True,
    )

    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "type": type(exc).__name__,
            },
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.environment,
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    Returns the health status of the service and its dependencies.
    """
    db_healthy = await check_db_connection()

    if not db_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
            },
        )

    return {
        "status": "healthy",
        "database": "connected",
    }


# TODO: Import and include routers
# from src.api.webhooks import twilio, whatsapp
# from src.api.v1 import calls, voices, health
#
# app.include_router(twilio.router, prefix="/webhooks/twilio", tags=["Twilio"])
# app.include_router(whatsapp.router, prefix="/webhooks/whatsapp", tags=["WhatsApp"])
# app.include_router(calls.router, prefix="/api/v1/calls", tags=["Calls"])
# app.include_router(voices.router, prefix="/api/v1/voices", tags=["Voices"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
