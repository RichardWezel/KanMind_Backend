from rest_framework import serializers

from auth_app.api.serializers import UserSerializer
from auth_app.models import CustomUser
from boards_app.models import Board
from tasks_app.api.serializers import TasksBoardDetailsSerializer


class BoardSerializer (serializers.ModelSerializer):
    """
    Serializer for creating and updating a board.

    Fields:
        - title: The name of the board (required).
        - members: A list of user IDs to be added as board members (write-only).
        - owner_id: The user who owns the board (read-only).
        - member_count, ticket_count, tasks_to_do_count, tasks_hight_prio_count:
          Counters related to board content (all read-only).

    Notes:
        The 'members' field accepts a list of user IDs.
        The owner is automatically assigned (usually the current user).
    """
   
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        write_only=True
    )
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members','member_count', 'ticket_count', 'tasks_to_do_count', 
                  'tasks_hight_prio_count', 'owner_id']
        read_only_fields = ['id', 'member_count', 'ticket_count', 'tasks_to_do_count', 
                            'tasks_hight_prio_count', 'owner_id']

    def validate_title(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Title must be a string.")
        if value.strip() == "":
            raise serializers.ValidationError("Title cannot be empty.")
        return value
    
    
class BoardDetailSerializer (serializers.ModelSerializer):
    """
    Serializer for retrieving detailed board information.

    Includes:
        - title: The board's title (read-only).
        - owner_id: The owner's user ID (read-only).
        - members: A list of user details (read-only).
        - tasks: A list of tasks assigned to the board (read-only).
    """

    members = UserSerializer(many=True)
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)
    tasks = TasksBoardDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating board data.

    Use cases:
        - Update the board's title.
        - Modify the list of member user IDs.

    Writeable:
        - title: The new board name.
        - members: List of user IDs to replace the current members.

    Read-only:
        - owner_data: The owner's user details.
        - members_data: A list of member user details.

    Notes:
        This serializer is typically used in PATCH requests.
    """
    
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        write_only=True
    )
    owner_data = UserSerializer(source='owner_id', read_only=True)
    members_data = UserSerializer(many=True, source='members', read_only=True)
   
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members', 'members_data']
        read_only_fields = ['id', 'owner_data', 'members_data']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False},
            'members': {'required': True}
        }
    