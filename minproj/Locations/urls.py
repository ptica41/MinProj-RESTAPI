from django.urls import path

from .views import LocationAPIView, LocationsAPIView


urlpatterns = [
    path('', LocationsAPIView.as_view()),
    path('<int:pk>/', LocationAPIView.as_view()),
]
