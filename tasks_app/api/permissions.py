from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as Forbidden
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound
from tasks_app.models import Task
from boards_app.models import Board 


class IsMemberOfBoard(BasePermission):
    """
    Erlaubt Zugriff nur für Mitglieder oder Owner des Boards.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Du musst angemeldet sein.")

        # Nur bei POST nötig – da haben wir noch kein Objekt
        if request.method == "POST":
            board_id = view.kwargs.get('board_id') or request.data.get('board')
            if not board_id:
                raise PermissionDenied("Board-ID fehlt.")

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise NotFound("Board existiert nicht.")

            if user not in board.members.all() and user != board.owner:
                raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return True  # für alle anderen Methoden erstmal OK

    def has_object_permission(self, request, view, obj):
        user = request.user
        owner = obj.board.owner_id
        # Zugriff auf das Task-Objekt → Board
        board = obj.board
        if user not in board.members.all() and user != owner:
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return True
        


