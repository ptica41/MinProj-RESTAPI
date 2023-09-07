from django.urls import path

from .views import LocationAPIView, LocationsAPIView


urlpatterns = [
    path('', LocationsAPIView.as_view()),
    path('<int:pk>/', LocationAPIView.as_view()),
]

#
# from .views import Locations, Create, Detail, Update, Delete
#
#
# urlpatterns = [
#     path('', Locations.as_view(), name='locations'),
#     path('create/', Create.as_view(), name='location_create'),
#     path('<int:pk>/update/', Update.as_view(), name='location_update'),
#     path('<int:pk>/delete/', Delete.as_view(), name='location_delete'),
#     path('<int:pk>/', Detail.as_view(), name='location'),
#    ]
