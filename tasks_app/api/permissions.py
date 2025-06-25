from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as Forbidden


class IsMemberOfBoard(BasePermission):
    """
    Erlaubt Zugriff nur für Mitglieder des Boards.
    Gibt bei Nichtmitgliedschaft eine benutzerdefinierte 403-Meldung zurück.
    """

    def has_permission(self, request, view):
        board_id = request.data.get('board')
        if not board_id:
            raise Forbidden("Board-ID fehlt.")

        try:
            from boards_app.models import Board
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise Forbidden("Das angegebene Board existiert nicht.")

        if request.user not in board.members.all():
            raise Forbidden("Verboten. Der Benutzer muss Mitglied des Boards sein.")

        return True
