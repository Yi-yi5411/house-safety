"""Custom exception classes for the application."""

from __future__ import annotations

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception with default status code."""

    def __init__(
        self,
        detail: str = "Internal server error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(AppException):
    """Raised when the user lacks permission."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_404_NOT_FOUND
        )


class ValidationError(AppException):
    """Raised when input validation fails."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class DuplicateError(AppException):
    """Raised when a unique constraint is violated."""

    def __init__(self, detail: str = "Duplicate entry") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)
