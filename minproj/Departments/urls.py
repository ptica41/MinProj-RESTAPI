from django.urls import path
# from .views import LogView
from django.contrib.auth.views import LogoutView

# from .views import Departments, LocationsDepartment
from .views import DepartmentAPIView, DepartmentsAPIView


urlpatterns = [
    path('', DepartmentsAPIView.as_view()),
    path('<int:pk>/', DepartmentAPIView.as_view()),
   ]
