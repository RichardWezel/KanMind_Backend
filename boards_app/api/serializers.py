from rest_framework import serializers

from auth_app.api.serializers import UserSerializer
from auth_app.models import CustomUser
from boards_app.models import Board
from tasks_app.api.serializers import TasksBoardDetailsSerializer


class BoardSerializer (serializers.ModelSerializer):
    """
    Serializer for creating and updating a board.
    It includes fields for the board's title, members, and owner.
    The 'members' field is a write-only field that allows the addition of members to the
    board during creation or update.
    The 'owner_id' field is read-only and represents the owner of the board.
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


class BoardDetailSerializer (serializers.ModelSerializer):
    """
    Serializer for retrieving board details.
    It includes the board's title, members, owner, and tasks.
    The 'members' field is read-only and returns a list of user details.
    The 'tasks' field returns a list of tasks associated with the board.
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
    Serializer for updating a board.
    It allows the owner to update the board's title and members.
    The 'members' field is a write-only field that allows the addition of members to the
    board during update.
    The 'owner_data' field is read-only and returns the owner's details.
    The 'members_data' field is read-only and returns a list of member details.
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
    