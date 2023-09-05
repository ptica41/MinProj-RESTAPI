from django.urls import path
# from .views import Detail, Operators, Update, Delete
from .views import RegistrationAPIView


urlpatterns = [
    # path('signup/', Register.as_view(template_name='../templates/signup.html'), name='signup'),
    # path('wait/', Wait.as_view(), name='wait'),
    path('signup/', RegistrationAPIView.as_view()),
    # path('<int:pk>/', Detail.as_view(), name='detail'),
    # path('<int:pk>/update/', Update.as_view(), name='update'),
    # path('<int:pk>/delete/', Delete.as_view(), name='delete'),
    # path('', Operators.as_view(), name='operators'),
]
