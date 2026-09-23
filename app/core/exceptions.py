"""Application-level exception hierarchy.

Feature services/repositories raise these instead of HTTPException directly, so
business logic stays framework-agnostic. The handlers registered in
`app.core.error_handlers` translate them into HTTP responses at the edge.
"""


class AppError(Exception):
    """Base class for all expected application errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.__class__.__doc__ or "An error occurred"
        super().__init__(self.detail)


class NotFoundError(AppError):
    """The requested resource was not found."""

    status_code = 404
    error_code = "not_found"


class AlreadyExistsError(AppError):
    """A resource with the given identifier already exists."""

    status_code = 409
    error_code = "already_exists"


class ValidationAppError(AppError):
    """The request failed a business-rule validation."""

    status_code = 422
    error_code = "validation_error"


class UnauthorizedError(AppError):
    """Authentication is required or credentials are invalid."""

    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(AppError):
    """The authenticated user is not allowed to perform this action."""

    status_code = 403
    error_code = "forbidden"


class ConflictError(AppError):
    """The request conflicts with the current state of the resource."""

    status_code = 409
    error_code = "conflict"


class ExternalServiceError(AppError):
    """A downstream dependency (Razorpay, Bedrock, ...) failed."""

    status_code = 502
    error_code = "external_service_error"
