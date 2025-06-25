from django.db import models
from auth_app.models import CustomUser
from boards_app.models import Board


class Task(models.Model):
    """
    Represents a task in the application.
    """
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('to-do', 'To-do'),
        ('in-progress', 'In-progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ], default='to_do')
    priority = models.CharField(max_length=50, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    assignee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks', blank=True, null=True) 
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviewed_tasks', blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['title'] 
