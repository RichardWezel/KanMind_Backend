from django.db import models
from boards_app.models import Board
from auth_app.models import CustomUser

class Task(models.Model):
    """
    Represents a task in the application.
    """
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('to_do', 'To-do'),
        ('in_progress', 'In-progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ], default='to_do')
    priority = models.CharField(max_length=50, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    assignee_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks', blank=True, null=True) 
    rewiewer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviewed_tasks', blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['created_at'] 
