from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response


def custom_exception_handler(exc, context):

    msg = exc.detail if hasattr(exc, 'detail') else str(exc)
    status = 403 if type(exc) in [NotAuthenticated, PermissionDenied] else 400
    return Response({'detail': msg}, status=status)
