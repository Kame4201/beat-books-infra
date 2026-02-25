"""
BeatTheBooks — Shared Contract Stubs

Copy this file into each app repo to enforce consistent response schemas.
These models align with docs/architecture/service-contracts.md.

Usage:
    cp beat-books-infra/templates/contract_stubs/contracts.py src/contracts.py

Source of truth: beat-books-infra/docs/architecture/service-contracts.md
"""

from typing import Any, List, Optional

from pydantic import BaseModel


# --- Standard Health Check (service-contracts.md §1) ---


class HealthResponse(BaseModel):
    """Standard health check response. All services must return this from GET /health."""

    status: str  # Always "healthy" if responding
    service: str  # e.g. "beat-books-data", "beat-books-model", "beat-books-api"
    version: str  # SemVer from pyproject.toml


# --- Standard Error Response (service-contracts.md §2) ---


class ErrorResponse(BaseModel):
    """Standard error response. All services must return errors in this format."""

    error: str  # Machine-readable error code (UPPER_SNAKE_CASE)
    detail: str  # Human-readable explanation
    status_code: int  # HTTP status code (mirrored in body)


# --- Pagination (service-contracts.md — used by /games, /standings) ---


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""

    data: List[Any]
    pagination: PaginationMeta
