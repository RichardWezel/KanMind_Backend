from django.urls import path, include
from .views import RegistrationView, CustomLoginView

# URL configuration for authentication endpoints.
#
# This module defines the routes for:
# - User registration via `RegistrationView`
# - User login via `CustomLoginView`
# - Browsable API login/logout using Django REST framework's built-in views

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
