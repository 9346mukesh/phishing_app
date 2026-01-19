"""Pydantic data models and schemas for API validation."""

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class URLInput(BaseModel):
    """URL input validation model."""

    url: str = Field(
        ...,
        description="URL to analyze for phishing",
        min_length=5,
        max_length=2048,
        example="https://example.com",
    )


class PredictionResponse(BaseModel):
    """API prediction response model."""

    prediction: int = Field(
        ...,
        description="Prediction: 0=Legitimate, 1=Phishing",
        ge=0,
        le=1,
    )
    confidence: float = Field(
        ...,
        description="Confidence score (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    label: str = Field(
        ...,
        description="Human-readable label",
    )
    url: str = Field(
        ...,
        description="Input URL that was analyzed",
    )
    features_count: int = Field(
        default=30,
        description="Number of features analyzed",
    )


class BatchPredictionRequest(BaseModel):
    """Batch prediction request model."""

    urls: List[str] = Field(
        ...,
        description="List of URLs to analyze",
        min_items=1,
        max_items=100,
    )


class BatchPredictionResponse(BaseModel):
    """Batch prediction response model."""

    results: List[PredictionResponse] = Field(
        ...,
        description="List of predictions",
    )
    total: int = Field(
        ...,
        description="Total number of URLs processed",
    )
    failed: int = Field(
        default=0,
        description="Number of failed predictions",
    )


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(
        ...,
        description="Service status",
    )
    version: str = Field(
        ...,
        description="Service version",
    )
    model_loaded: bool = Field(
        ...,
        description="Whether model is loaded",
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(
        ...,
        description="Error message",
    )
    detail: Optional[str] = Field(
        default=None,
        description="Additional error details",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for tracking",
    )
