from rest_framework import serializers

from tasks_app.models import Task, TaskComment
from auth_app.api.serializers import UserSerializer
from auth_app.models import CustomUser

def user_field():
    """
    Returns a serializer field for the user, which is read-only and returns user details.
    This field is used for the 'assignee' and 'reviewer' fields in the TaskSerializer.
    """
    return UserSerializer(read_only=True)

def pk_field_for(source_name):
    """
    Returns a PrimaryKeyRelatedField for the specified source name.
    This field
    is used for the 'assignee_id' and 'reviewer_id' fields in the TaskCreateSerializer and TaskUpdateSerializer.
    It allows for the assignment of a user by their primary key.
    """
    return serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source=source_name,
        write_only=True,
        required=False,       
        allow_null=True   
    )

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying task data.

    Includes task information such as:
    - title, description, status, priority
    - read-only user info for assignee and reviewer
    - due date and comment count
    """

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


class TasksBoardDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying tasks inside board detail views.

    Includes:
    - full task information
    - assignee and reviewer as nested user data
    """
   
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


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new task.

    Accepts:
    - board, title, description, status, priority
    - optional assignee_id and reviewer_id as user PKs
    - optional due date
    """

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
    """
    Serializer for updating an existing task.

    Accepts:
    - all fields of a task, including assignee and reviewer (by user ID)
    Returns:
    - nested user objects for assignee and reviewer
    """

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
        """
        Update all task fields with incoming validated data.
        """

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
    """
    Serializer for displaying task comments.

    Includes:
    - comment content
    - creation timestamp
    - author's full name (read-only)
    """
    
    author = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']
    
    def get_author(self, obj):
        return obj.author.fullname  
    