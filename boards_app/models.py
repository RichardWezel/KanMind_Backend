from django.db import models
from auth_app.models import CustomUser 
from tasks_app.models import Task

class Board(models.Model):
    """
    Represents a board in the application.
    """
    title = models.CharField(max_length=255, unique=True, help_text="Name of the board")
    member_count = models.PositiveIntegerField(default=0, help_text="Number of members in the board")
    ticket_count = models.PositiveIntegerField(default=0, help_text="Number of tickets to do")
    tasks_to_do_count = models.PositiveIntegerField(default=0, help_text="Number of tasks to do")
    tasks_hight_prio_count = models.PositiveIntegerField(default=0, help_text="Number of high priority tasks")
    owner_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='boards')
    members = models.ManyToManyField(CustomUser, verbose_name=("users"), related_name='board_members', blank=True, help_text="Users who are members of the board")
    tasks = models.ManyToManyField('tasks_app.Task', verbose_name=("tasks"), related_name='board_tasks', blank=True, help_text="Tasks associated with the board")
    rewiewers = models.ManyToManyField(CustomUser, verbose_name=("reviewers"), related_name='board_reviewers', blank=True, help_text="Users who can review tasks in the board")
    due_date = models.DateField(null=True, blank=True, help_text="Due date for the board tasks")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ['title']