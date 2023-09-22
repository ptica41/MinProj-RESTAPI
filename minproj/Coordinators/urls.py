from django.urls import path
from .views import RegistrationAPIView


app_name = 'Coordinators'
urlpatterns = [
    path('signup/', RegistrationAPIView.as_view()),
]
