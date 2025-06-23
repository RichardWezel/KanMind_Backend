from rest_framework import serializers
from boards_app.models import Board
from auth_app.models import CustomUser
from auth_app.api.serializers import UserSerializer

class BoardSerializer (serializers.ModelSerializer):
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
    members = UserSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)
    tasks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'title', 'owner_id', 'members', 'tasks']