from django.contrib import admin
from django.urls import path, include

from .views import TaskAssignedToMeView, TaskReviewingView
from tasks_app.api.views import CreateTaskView, TaskDetailView, TaskCreateCommentView, TaskDeleteCommentView

# URL configuration for task-related API endpoints.
#
# Endpoints:
# - POST   /                       → Create a new task (CreateTaskView)
# - GET    /assigned-to-me/       → List tasks assigned to the current user (TaskAssignedToMeView)
# - GET    /reviewing/            → List tasks where the current user is the reviewer (TaskReviewingView)
# - PATCH  /<int:pk>/             → Update a specific task by ID (TaskDetailView)
# - POST   /<int:pk>/comments/    → Add a comment to a task (TaskCreateCommentView)
# - DELETE /<int:task_id>/comments/<int:comment_id> → Delete a specific comment from a task (TaskDeleteCommentView)

urlpatterns = [
    path('', CreateTaskView.as_view(), name='task-create'),
    path('assigned-to-me/', TaskAssignedToMeView.as_view(), name='assigned-to-me'),
    path('reviewing/', TaskReviewingView.as_view(), name='task-reviewing'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/comments/', TaskCreateCommentView.as_view(), name='task-comments'),
    path('<int:task_id>/comments/<int:comment_id>/', TaskDeleteCommentView.as_view(), name='task-delete-comment'),
]


