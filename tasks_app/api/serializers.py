from rest_framework import serializers
from tasks_app.models import Task
from auth_app.api.serializers import UserSerializer
from auth_app.models import CustomUser
from boards_app.models import Board
from boards_app.api.serializers import BoardSerializer


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(
        read_only=True
    )
    reviewer = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 
            'priority', 'assignee', 'reviewer', 
            'due_date', 'comments_count'
        ]
        read_only_fields = ['id', 'comments_count']

class TaskCreateSerializer(serializers.ModelSerializer):

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='assignee',
        write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='reviewer',
        write_only=True
    )
    
    class Meta:
        model = Task
        fields = [
            'board', 'title', 'description', 'status', 
            'priority', 'assignee_id', 'reviewer_id', 
            'due_date'
        ]
    
    def create(self, validated_data):
        return Task.objects.create(**validated_data)