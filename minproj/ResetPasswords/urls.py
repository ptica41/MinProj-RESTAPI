from django.urls import path
from .views import MyResetPasswordRequestToken, ListReset, MyResetPasswordConfirm


app_name = 'ResetPasswords'
urlpatterns = [
    path('', MyResetPasswordRequestToken.as_view()),
    path('confirm/', MyResetPasswordConfirm.as_view()),
    path('list/', ListReset.as_view()),
]
