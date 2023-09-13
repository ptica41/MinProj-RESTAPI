from django.urls import path

from .views import EventAPIView, EventsAPIView


urlpatterns = [
    path('', EventsAPIView.as_view()),
    path('<int:pk>/', EventAPIView.as_view()),
]