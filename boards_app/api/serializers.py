from rest_framework import serializers
from boards_app.models import Board
from auth_app.models import CustomUser
from auth_app.api.serializers import UserSerializer
from tasks_app.api.serializers import TasksBoardDetailsSerializer


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
    members = UserSerializer(many=True)
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)
    tasks = TasksBoardDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
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
    