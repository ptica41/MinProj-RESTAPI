from django.urls import path
from .views import Detail, UpdateByRecipient, UpdateByCoordinator, Delete, Recipients, EventsToRecipient
from .views import RegistrationAPIView

urlpatterns = [
    # path('signup/', Register.as_view(template_name='../templates/signup.html'), name='signup'),
    # path('wait/', Wait.as_view(), name='wait'),
    path('signup/', RegistrationAPIView.as_view()),
    path('<int:pk>/', Detail.as_view(), name='detail'),
    path('<int:pk>/update/', UpdateByRecipient.as_view(), name='update'),
    path('<int:pk>/edit/', UpdateByCoordinator.as_view(), name='edit'),
    path('<int:pk>/delete/', Delete.as_view(), name='delete'),
    path('<int:pk>/events/', EventsToRecipient.as_view(), name='events_to_recipient'),
    path('', Recipients.as_view(), name='recipients'),
]
