from django.urls import path
# from .views import LogView
from django.contrib.auth.views import LogoutView

from .views import GroupsAPIView, GroupAPIView, GroupUsersAPIView


urlpatterns = [
    path('', GroupsAPIView.as_view()),
    path('<int:pk>/', GroupAPIView.as_view()),
    path('<int:pk>/users/', GroupUsersAPIView.as_view()),
   ]
