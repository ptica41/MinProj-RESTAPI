from django.urls import path
from .views import Detail, Update, Delete, Coordinators
from .views import RegistrationAPIView


app_name = 'Coordinators'
urlpatterns = [
    # path('signup/', Register.as_view(template_name='../templates/signup.html'), name='signup'),
    path('signup/', RegistrationAPIView.as_view()),
    # path('wait/', Wait.as_view(), name='wait'),
    path('<int:pk>/', Detail.as_view(), name='detail'),
    path('<int:pk>/update/', Update.as_view(), name='update'),
    path('<int:pk>/delete/', Delete.as_view(), name='delete'),
    path('', Coordinators.as_view(), name='coordinators'),
]
