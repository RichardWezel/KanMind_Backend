from django.db import models
from auth_app.models import CustomUser
from boards_app.models import Board


class Task(models.Model):
    """
    Represents a task within a board.

    A task can have a title, description, status, priority,
    an optional assignee and reviewer, and an optional due date.

    Relationships:
        - Belongs to a Board
        - May be assigned to a User
        - May be reviewed by a User
    """

    STATUS_TODO = 'to-do'
    STATUS_IN_PROGRESS = 'in-progress'
    STATUS_REVIEW = 'review'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_TODO, 'To-do'),
        (STATUS_IN_PROGRESS, 'In-progress'),
        (STATUS_REVIEW, 'Review'),
        (STATUS_DONE, 'Done'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_TODO)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    assignee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks', blank=True, null=True) 
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviewed_tasks', blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        """
        Return the string representation of the task.
        """
        return self.title

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['title'] 

class TaskComment(models.Model):
    """
    Represents a comment made by a user on a task.

    Relationships:
        - Belongs to a Task
        - Has an author (User)
    """

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        """
        Return the first 50 characters of the comment for display.
        """
        return self.content[:50]  

    class Meta:
        verbose_name = "Task-Comment"
        verbose_name_plural = "Task-Comments"
        ordering = ['created_at'] 