from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('', include('Minapp.urls')),
    path('departments/', include('Departments.urls')),
    path('groups/', include('Groups.urls')),
    path('coordinators/', include('Coordinators.urls')),
    path('recipients/', include('Recipients.urls')),
    path('operators/', include('Operators.urls')),
    path('locations/', include('Locations.urls')),
    path('events/', include('Events.urls')),
    path('password-reset/', include('ResetPasswords.urls')),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
