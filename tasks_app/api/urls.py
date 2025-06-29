from django.contrib import admin
from django.urls import path, include
from auth_app.api.views import RegistrationView, CustomLoginView
from boards_app.api.views import BoardView, BoardDetailView
from .views import TaskAssignedToMeView, TaskReviewingView
from tasks_app.api.views import CreateTaskView, TaskUpdateView

urlpatterns = [
    path('', CreateTaskView.as_view(), name='task-create'),
    path('assigned-to-me/', TaskAssignedToMeView.as_view(), name='assigned-to-me'),
    path('reviewing/', TaskReviewingView.as_view(), name='task-reviewing'),
    path('<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
]


