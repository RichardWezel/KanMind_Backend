from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as Forbidden


from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from tasks_app.models import Task
from boards_app.models import Board


class IsMemberOfBoard(BasePermission):
    """
    Erlaubt Zugriff nur für Mitglieder des Boards – entweder über direkte board-ID (POST)
    oder über die Task-Instanz (PUT/PATCH).
    """

    def has_permission(self, request, view):
        user = request.user

        # 🔁 Bei POST: Board-ID muss im Body sein
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                raise PermissionDenied("Board-ID fehlt.")

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise PermissionDenied("Board existiert nicht.")

        # 🛠 Bei PUT/PATCH/DELETE: Board über Task-Objekt holen
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            try:
                task = view.get_object()
                board = task.board
            except Task.DoesNotExist:
                raise PermissionDenied("Task existiert nicht.")
            except Exception:
                raise PermissionDenied("Zugriff verweigert.")

        else:
            return True  # GET etc.

        if user not in board.members.all() and user != board.owner_id:
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return True

