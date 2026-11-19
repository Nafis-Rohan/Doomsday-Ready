from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ApiError(APIException):
    """Base class for our errors. Carries a machine-readable code."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "VALIDATION_ERROR"
    default_detail = "Invalid request."

    def __init__(self, message=None, code=None, details=None):
        super().__init__(detail=message, code=code)
        self.error_code = code or self.default_code
        self.error_details = details or {}


class CircularDependency(ApiError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "CIRCULAR_DEPENDENCY"
    default_detail = "This change would create a circular dependency."


class DuplicateTitle(ApiError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "DUPLICATE_TITLE"
    default_detail = "A movie with this title already exists."


class DuplicateName(ApiError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "DUPLICATE_NAME"
    default_detail = "A cinema with this name already exists."


class UnknownPrerequisite(ApiError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "UNKNOWN_PREREQUISITE"
    default_detail = "A prerequisite does not match any existing movie."


class InvalidGroupSize(ApiError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "INVALID_GROUP_SIZE"
    default_detail = "groupSize must be a whole number from 1 to 10,000."


_CODES_BY_STATUS = {
    400: "VALIDATION_ERROR",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    415: "UNSUPPORTED_MEDIA_TYPE",
}


def api_exception_handler(exc, context):
    """Turn every error into {"error": {"code", "message", "details"}}."""
    if isinstance(exc, ApiError):
        return Response(
            {
                "error": {
                    "code": exc.error_code,
                    "message": str(exc.detail),
                    "details": exc.error_details,
                }
            },
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        return None  # not an API error: let Django return a 500

    if isinstance(exc, ValidationError):
        message = "Invalid input."
        details = response.data
        if not isinstance(details, dict):
            details = {"non_field_errors": details}
    else:
        message = str(response.data.get("detail", "Request failed."))
        details = {}

    response.data = {
        "error": {
            "code": _CODES_BY_STATUS.get(response.status_code, "ERROR"),
            "message": message,
            "details": details,
        }
    }
    return response