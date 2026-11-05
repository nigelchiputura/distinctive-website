"""Errors services raise. Controllers map them to responses (BaseController); services never
raise Http404 or return responses (docs/architecture.md §4)."""


class ServiceError(Exception):
    """Base class. `message` is safe to show to a visitor."""

    status_code = 500
    default_message = "Something went wrong."

    def __init__(self, message: str | None = None, errors: dict[str, list[str]] | None = None):
        self.message = message or self.default_message
        self.errors = errors or {}
        super().__init__(self.message)


class NotFoundError(ServiceError):
    status_code = 404
    default_message = "We couldn't find that page."


class ValidationError(ServiceError):
    """Bad input. `errors` maps field names to messages ("__all__" for the form as a whole)."""

    status_code = 400
    default_message = "Please check the details and try again."


class ExternalServiceError(ServiceError):
    """A provider we depend on (email, maps) failed in a way the visitor should hear about."""

    status_code = 503
    default_message = "That didn't work just now. Please try again in a few minutes."
