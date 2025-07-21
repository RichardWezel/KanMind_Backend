from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

class IsAuthenticatedWithCustomMessage(BasePermission):
    """
    Custom permission to only allow authenticated users.
    If the user is not authenticated, it raises a NotAuthenticated error with a custom message.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="Not authorized. The user must be logged in.")
        return True

class IsOwnerOrMemberOfBoard(BasePermission):
    """
    Custom permission to allow access only to the owner or members of a board.
    If the user is not the owner or a member, it raises a PermissionDenied error.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user == obj.owner or user in obj.members.all():
            return True
        
        raise PermissionDenied()
