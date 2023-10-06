from django.urls import path
from .views import MyResetPasswordRequestToken, ListReset

from django_rest_passwordreset.views import ResetPasswordConfirm

app_name = 'ResetPasswords'
urlpatterns = [
    path('', MyResetPasswordRequestToken.as_view()),
    path('confirm/', ResetPasswordConfirm.as_view()),
    path('list/', ListReset.as_view()),
]
