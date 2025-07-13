from rest_framework import serializers
from tasks_app.models import Task, TaskComment
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
        write_only=True,
        required=False,       
        allow_null=True   
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
    status = serializers.ChoiceField(
        choices=Task.STATUS_CHOICES,
        default=Task.STATUS_TODO
    )
    priority = serializers.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        default=Task.PRIORITY_LOW
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
    

class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    assignee = user_field()
    reviewer = user_field()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'priority', 'assignee', 'assignee_id',
            'reviewer', 'reviewer_id',
            'due_date'
        ]
        read_only_fields = ['id']
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.assignee = validated_data.get('assignee', instance.assignee)
        instance.reviewer = validated_data.get('reviewer', instance.reviewer)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.save()
        return instance

class TaskCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']
    
    def get_author(self, obj):
        return obj.author.fullname  
    