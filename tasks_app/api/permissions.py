from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as Forbidden
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound

from tasks_app.models import Task
from boards_app.models import Board 


class IsMemberOfBoard(BasePermission):
    """
    Permission class that allows access only to members or the owner of a board.
    - For POST requests, checks if the user is authenticated and a member or owner of the specified board.
    - For other methods, allows access by default.
    - For object-level permissions, ensures the user is a member or owner of the board associated with the object.
    Raises:
        PermissionDenied: If the user is not authenticated, not a member, or not the owner.
        NotFound: If the specified board does not exist.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Du musst angemeldet sein.")

        # Nur bei POST nötig – da haben wir noch kein Objekt
        if request.method == "POST":

            board_id = view.kwargs.get('board_id') or request.data.get('board')
            if not board_id:
                raise PermissionDenied("Du bist nicht Mitglied des Boards.")

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
        
class IsMemberOfBoardComments(BasePermission):
    """
    Permission class that allows access to comments only for members or the owner of the board.
    - Checks if the user is authenticated and a member or owner of the board associated with the
    comment.
    - Raises PermissionDenied if the user is not authenticated, not a member, or not the
    owner of the board.
    - Raises NotFound if the specified task does not exist.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Du musst angemeldet sein.")

        task_id = view.kwargs.get("pk")  # wird aus der URL geholt
        if not task_id:
            raise PermissionDenied("Task-ID fehlt.")

        try:
            task = Task.objects.select_related("board").get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task existiert nicht.")

        board = task.board
        if user not in board.members.all() and user.id != board.owner_id:
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return True
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        owner = obj.board.owner_id
        # Zugriff auf das Task-Objekt → Board
        board = obj.board
        if user not in board.members.all() and user.id != board.owner_id:
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return True

class IsAuthorOfComment(BasePermission):
    """
    Permission class that allows access to comments only for the author of the comment.
    - Checks if the user is the author of the comment.
    - Raises PermissionDenied if the user is not the author.
    """

    def has_object_permission(self, request, view, obj):
        if request.user != obj.author:
            raise PermissionDenied("Du darfst nur deine eigenen Kommentare löschen.")
        return True