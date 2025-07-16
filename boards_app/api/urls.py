from django.urls import path

from boards_app.api.views import BoardView, BoardDetailView

# URL configuration for board-related API endpoints.
#
# Available endpoints:
# - GET /         → List all boards
# - POST /        → Create a new board
# - GET /<int:pk>/ → Retrieve details of a specific board
# - PATCH /<int:pk>/ → Update a specific board (partial update)
# - DELETE /<int:pk>/ → Delete a specific board

urlpatterns = [
    path('', BoardView.as_view(), name='boards'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'), 
]

 