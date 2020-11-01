import os

from rest_framework.permissions import BasePermission


class IsArtexchange(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        artexchange_email = os.getenv('ARTEXCHANGE_EMAIL')
        return user.is_authenticated and user.email == artexchange_email


class IsXendAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == 'System Admin'


