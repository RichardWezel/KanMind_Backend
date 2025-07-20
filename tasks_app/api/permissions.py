from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as Forbidden
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.exceptions import ValidationError

from tasks_app.models import Task
from boards_app.models import Board 


class IsMemberOfBoard(BasePermission):
    """
    Allows access only to members or the owner of a board.

    Use cases:
    - On POST: Checks whether the user is a member or the owner of the board (via board ID).
    - On other methods: Grants permission.
    - On object level: Checks if the user is related to the task's board.

    Raises:
        PermissionDenied: If the user is not a member or the owner.
        NotFound: If the specified board does not exist.
    """

    def has_permission(self, request, view):
        """
        Check global permissions for a request.

        - For POST: ensure the user is a member or the owner of the specified board.
        - For other methods: allow access (object-level check will apply).
        """
        print(f"[DEBUG] has_permission called for {request.method} by {request.user}")
        if request.method == "POST":
            board_id = request.data.get("board")
            try:
                board_id = int(board_id)
            except (TypeError, ValueError):
                raise ValidationError({"board": "Board must be a valid integer ID."})

            if not Board.objects.filter(id=board_id).exists():
                raise NotFound("Board not found.")

            board = Board.objects.get(id=board_id)
            if request.user not in board.members.all() and board.owner_id != request.user.id:
                return False
            return True

        return True


    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        The user must be a member or the owner of the board linked to the task.

        Returns:
            bool: True if access is granted.
        """

        user = request.user
        owner = obj.board.owner_id
        board = obj.board
        if user not in board.members.all() and user != owner:
            raise PermissionDenied("You are not a member of this board.")

        return True
        
class IsMemberOfBoardComments(BasePermission):
    """
    Allows access to task comments only for board members or the owner.

    Use cases:
    - Requires the user to be authenticated and part of the board that owns the task.
    - Validates task ID from the URL.

    Raises:
        PermissionDenied: If user lacks permission.
        NotFound: If the task doesn't exist.
    """

    task_lookup_kwarg = 'task_id'  # default, kann in View überschrieben werden

    def has_permission(self, request, view):
        """
        Check permission for comment access based on task and board membership.

        Returns:
            bool: True if the user has permission.
        """

        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in.")
        
        # Konfigurierbaren URL-Parameternamen holen
        lookup_kwarg = getattr(view, 'task_lookup_kwarg', self.task_lookup_kwarg)
        task_id = view.kwargs.get(lookup_kwarg)
        if not task_id:
            raise PermissionDenied("Task-id is missing.")

        try:
            task = Task.objects.select_related("board").get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task does not exist.")

        board = task.board
        if user not in board.members.all() and user.id != board.owner_id:
            raise PermissionDenied("You are not a member of this board.")

        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permission for comments on a task.

        Returns:
            bool: True if the user is authorized.
        """

        user = request.user
        board = obj.task.board
        if user not in board.members.all() and user.id != board.owner_id:
            raise PermissionDenied("You are not a member of this board.")
        return True

class IsAuthorOfComment(BasePermission):
    """
    Check object-level permission based on comment author.
    Returns:
        bool: True if the request user is the comment's author.
    """

    def has_object_permission(self, request, view, obj):
        if request.user != obj.author:
            raise PermissionDenied("You are not the author of this comment.")
        return True