from django.urls import path
# from .views import LogView
from django.contrib.auth.views import LogoutView

# from .views import Departments, LocationsDepartment
from .views import DepartmentAPIView, DepartmentsAPIView, DepartmentLocationsAPIView


urlpatterns = [
    path('', DepartmentsAPIView.as_view()),
    path('<int:pk>/', DepartmentAPIView.as_view()),
    path('<int:pk>/locations/', DepartmentLocationsAPIView.as_view()),
   ]
