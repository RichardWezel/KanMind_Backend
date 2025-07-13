from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as Forbidden


from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound
from tasks_app.models import Task
from boards_app.models import Board


from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from tasks_app.models import Task
from boards_app.models import Board


class IsMemberOfBoard(BasePermission):
    """
    Erlaubt Zugriff nur für Mitglieder oder Owner des Boards.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Du musst angemeldet sein, um auf diese Ressource zuzugreifen.")

        board_id = view.kwargs.get('board_id') or request.data.get('board')

        if not board_id:
            raise PermissionDenied("Board-ID fehlt.")

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board existiert nicht.")

        owner = board.owner_id  
        if user not in board.members.all() and user != owner:
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return True
        


