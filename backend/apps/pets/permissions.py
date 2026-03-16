from rest_framework import permissions
from apps.users.constants import UserModelChoices


class IsOwnerOrAdminOrSupport(permissions.BasePermission):
    """Allow access to the pet owner, admin, or support staff."""

    def has_object_permission(self, request, view, obj):
        if request.user.role in (UserModelChoices.ROLE_CHOICES.ADMIN, UserModelChoices.ROLE_CHOICES.SUPPORT):
            return True
        return obj.owner == request.user


class IsCustomer(permissions.BasePermission):
    """Only allow customers to perform the action."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserModelChoices.ROLE_CHOICES.CUSTOMER


class IsSupportOrAdmin(permissions.BasePermission):
    """Only allow support or admin users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (UserModelChoices.ROLE_CHOICES.SUPPORT, UserModelChoices.ROLE_CHOICES.ADMIN)
