from django.urls import path

from .views import LoginAPIView, WhoAmIView, UsersAPIView, UserAPIView, CoordinatorsAPIView, OperatorsAPIView, \
    RecipientsAPIView, UserGroupsAPIView, UserEventsAPIView, GetPhoto, UploadPhoto


urlpatterns = [
    path('auth/signin/', LoginAPIView.as_view()),
    path('whoami/', WhoAmIView.as_view()),
    path('users/', UsersAPIView.as_view()),
    path('users/<int:pk>/', UserAPIView.as_view()),
    path('users/<int:pk>/groups/', UserGroupsAPIView.as_view()),
    path('users/<int:pk>/events/', UserEventsAPIView.as_view()),
    path('users/coordinators/', CoordinatorsAPIView.as_view()),
    path('users/operators/', OperatorsAPIView.as_view()),
    path('users/recipients/', RecipientsAPIView.as_view()),
    path('photo/<str>/', GetPhoto.as_view()),
    path('upload-photo/', UploadPhoto.as_view()),
]
