from rest_framework import serializers
from tasks_app.models import Task
from auth_app.api.serializers import UserSerializer
from auth_app.models import CustomUser


# Serializer for user field to be reused in multiple serializers
def user_field():
    return UserSerializer(read_only=True)


# Serializer for user field with write-only primary key related field
def pk_field_for(source_name):
    return serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source=source_name,
        write_only=True
    )


# Serializers for Task model
class TaskSerializer(serializers.ModelSerializer):
    assignee = user_field()
    reviewer = user_field()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 
            'priority', 'assignee', 'reviewer', 
            'due_date', 'comments_count'
        ]
        read_only_fields = ['id', 'comments_count']


# Serializer for Task details in a board
class TasksBoardDetailsSerializer(serializers.ModelSerializer):
    assignee = user_field()
    reviewer = user_field()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'priority', 'assignee', 'reviewer', 
            'due_date', 'comments_count'
        ]
        read_only_fields = ['id', 'comments_count']


# Serializer for creating a new Task
class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = pk_field_for('assignee')
    reviewer_id = pk_field_for('reviewer')
    
    class Meta:
        model = Task
        fields = [
            'board', 'title', 'description', 'status', 
            'priority', 'assignee_id', 'reviewer_id', 
            'due_date'
        ]
    
    def create(self, validated_data):
        return Task.objects.create(**validated_data)