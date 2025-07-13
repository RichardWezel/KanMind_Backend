from django.urls import path

from boards_app.api.views import BoardView, BoardDetailView

urlpatterns = [
    path('', BoardView.as_view(), name='boards'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'), 
]

 