from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board', 'assignee', 'reviewer', 'status', 'priority', 'due_date', 'comments_count')
    search_fields = ('title',)
    list_filter = ('status', 'priority')
    ordering = ('-id',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('board', 'assignee', 'reviewer')

# Register your models here.
