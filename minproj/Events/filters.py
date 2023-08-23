import django_filters
from django_filters import FilterSet

from Minapp.models import Event, Location, Recipient


class EventFilter(FilterSet):
    location_id = django_filters.ModelChoiceFilter(queryset=Location.objects.filter(is_active=True))
    recipient_id = django_filters.ModelChoiceFilter(queryset=Recipient.objects.filter(is_active=True))

    class Meta:
        model = Event
        fields = ['is_check', 'is_finished', 'datetime', 'location_id', 'recipient_id']
