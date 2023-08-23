from django.urls import path
# from .views import LogView
from django.contrib.auth.views import LogoutView

from .views import Departments, LocationsDepartment
from .views import LoginAPIView


urlpatterns = [
    # path('login/', LogView.as_view(template_name='login.html'), name='login'),
    path('auth/signin/', LoginAPIView.as_view()),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('departments/', Departments.as_view(), name='departments'),
    path('departments/<int:pk>/locations', LocationsDepartment.as_view(), name='locations_department'),
   ]
