"""FastAPI application for production serving."""

import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from src.phishing.config.settings import settings
from src.phishing.core.detector import DetectionError, PhishingDetector
from src.phishing.models.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    ErrorResponse,
    HealthResponse,
    PredictionResponse,
    URLInput,
)
from src.phishing.utils.logging_config import get_logger, safe_error_message
from src.phishing.utils.validators import URLValidationError

logger = get_logger("api")

# Global detector instance
detector: Optional[PhishingDetector] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown."""
    global detector
    # Startup
    logger.info("Starting up API server...")
    try:
        detector = PhishingDetector(auto_load=True)
        logger.info("Detector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize detector: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down API server...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Production-ready API for phishing website detection",
        version=settings.app_version,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,
    )

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=settings.app_name,
            version=settings.app_version,
            description="Real-time phishing URL detection API",
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {"url": "https://example.com/logo.png"}
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(time.time()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Routes
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint - API information."""
        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "message": "Phishing Detection API is operational",
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "predict": "/predict",
                "batch": "/predict-batch",
                "info": "/info"
            }
        }

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy" if detector and detector.is_ready else "unhealthy",
            version=settings.app_version,
            model_loaded=detector is not None and detector.is_ready,
        )

    @app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
    async def predict(request: URLInput):
        """
        Predict if a URL is phishing.

        Args:
            request: URLInput with URL to analyze

        Returns:
            PredictionResponse with prediction, confidence, and label
        """
        if not detector or not detector.is_ready:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Service unavailable.",
            )

        try:
            prediction, confidence, label = detector.predict(request.url)

            return PredictionResponse(
                prediction=prediction,
                confidence=confidence,
                label=label,
                url=request.url,
            )

        except URLValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=safe_error_message(e),
            ) from e
        except DetectionError as e:
            logger.error(f"Detection error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=safe_error_message(e),
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred",
            ) from e

    @app.post("/predict-batch", response_model=BatchPredictionResponse, tags=["Prediction"])
    async def predict_batch(request: BatchPredictionRequest):
        """
        Predict multiple URLs in batch.

        Args:
            request: BatchPredictionRequest with list of URLs

        Returns:
            BatchPredictionResponse with results
        """
        if not detector or not detector.is_ready:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Service unavailable.",
            )

        try:
            results = detector.predict_batch(request.urls)

            # Separate successful and failed predictions
            successful = [r for r in results if r.get("status") == "success"]
            failed = [r for r in results if r.get("status") == "failed"]

            # Convert to PredictionResponse objects for successful ones
            prediction_responses = [PredictionResponse(**r) for r in successful]

            return BatchPredictionResponse(
                results=prediction_responses,
                total=len(request.urls),
                failed=len(failed),
            )

        except Exception as e:
            logger.error(f"Batch prediction error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Batch prediction failed",
            ) from e

    @app.get("/info", tags=["System"])
    async def get_info():
        """Get system information."""
        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "detector": detector.get_info() if detector else None,
        }

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Custom HTTP exception handler."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail,
                request_id=getattr(request.state, "request_id", None),
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """General exception handler."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="An unexpected error occurred",
                request_id=getattr(request.state, "request_id", None),
            ).dict(),
        )

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.phishing.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
