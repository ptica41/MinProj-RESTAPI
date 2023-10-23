from django.urls import path

from .views import GroupsAPIView, GroupAPIView, GroupUsersAPIView, GroupManyUsersAPIView


urlpatterns = [
    path('', GroupsAPIView.as_view()),
    path('<int:pk>/', GroupAPIView.as_view()),
    path('<int:pk>/users/', GroupUsersAPIView.as_view()),
    path('<int:pk>/users/many/', GroupManyUsersAPIView.as_view()),
   ]
