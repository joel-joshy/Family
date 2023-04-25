from rest_framework.permissions import IsAuthenticated

from apps.usermanagement.models import User


class IsAnyManager(IsAuthenticated):

    def has_permission(self, request, view):
        return request.user.user_type in [User.ADMIN, User.MANAGER]