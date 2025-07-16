from django.contrib import admin
from django.urls import path, include
from boards_app.api.views import EmailCheckView

# Root URL configuration for the project.
#
# Routes:
# - /admin/ → Django admin interface
# - /api/ → Authentication routes (e.g., login, registration)
# - /api/boards/ → Board management endpoints
# - /api/email-check/ → Endpoint to check if an email is already in use
# - /api/tasks/ → Task-related endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/boards/', include('boards_app.api.urls')),
    path('api/email-check/', EmailCheckView.as_view(), name='email-check'),
    path('api/tasks/', include('tasks_app.api.urls')), 
]
