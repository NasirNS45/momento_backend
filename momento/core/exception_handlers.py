from ninja.errors import ValidationError
from ninja.responses import Response


def validation_error_handler(request, exception: ValidationError):
    formatted_errors = {}
    for error in exception.errors:
        for key, value in error.items():
            formatted_errors[key] = value
    return Response(formatted_errors, status=422)
