import datetime

from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect

from Minapp.models import Event, Operator, Recipient, Coordinator
from .forms import EventForm, EventUpdateForm, EventUpdateFormByCoordinator
from .filters import EventFilter


class PassRequestToFormViewMixin:  # Класс для добавления request-данных в форму создания локации
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class Create(UserPassesTestMixin, PassRequestToFormViewMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['operator'] = Operator.objects.get(user_id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        return context

    def test_func(self):
        try:
            operator = Operator.objects.get(user_id=self.request.user.id)
            return operator.is_check and operator.is_active
        except Operator.DoesNotExist:
            return False


class Detail(UserPassesTestMixin, DetailView):
    model = Event
    template_name = 'event.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
        except Coordinator.DoesNotExist:
            pass
        try:
            context['operator'] = Operator.objects.get(user_id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        try:
            context['recipient'] = Recipient.objects.get(id=self.request.user.id)
        except Recipient.DoesNotExist:
            pass
        return context

    def test_func(self):
        try:
            if self.request.user.staff == 'CO':
                try:
                    coordinator = Coordinator.objects.get(user_id=self.request.user.id)
                    return coordinator.is_check and coordinator.is_active
                except Coordinator.DoesNotExist:
                    return False
            elif self.request.user.staff == 'OP':
                try:
                    operator = Operator.objects.get(user_id=self.request.user.id)
                    return operator.is_check and operator.is_active
                except Operator.DoesNotExist:
                    return False
            elif self.request.user.staff == 'RE':
                try:
                    recipient = Recipient.objects.get(user_id=self.request.user.id)
                    event = Event.objects.get(id=self.kwargs.get('pk'))
                    return recipient.is_check and recipient.is_active and recipient == event.recipient_id
                except Operator.DoesNotExist:
                    return False
        except AttributeError:
            return False


class Update(UserPassesTestMixin, PassRequestToFormViewMixin, UpdateView):
    model = Event
    form_class = EventUpdateForm
    template_name = 'event_update.html'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['operator'] = Operator.objects.get(user_id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        return context


    def test_func(self):
        try:
            operator = Operator.objects.get(user_id=self.request.user.id)
            event = Event.objects.get(id=self.kwargs.get('pk'))
            return operator.is_check and operator.is_active and operator.department_id == event.location_id.department_id
        except Operator.DoesNotExist:
            return False


class UpdateByCoordinator(UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventUpdateFormByCoordinator
    template_name = 'event_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['event'] = Event.objects.get(id=self.kwargs.get('pk'))
        except Event.DoesNotExist:
            pass
        try:
            context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
        except Coordinator.DoesNotExist:
            pass
        return context

    def test_func(self):
        try:
            coordinator = Coordinator.objects.get(user_id=self.request.user.id)
            return coordinator.is_check and coordinator.is_active
        except Coordinator.DoesNotExist:
            return False


class Delete(UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'event_delete.html'
    context_object_name = 'event'
    success_url = '/events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['operator'] = Operator.objects.get(user_id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        return context

    def test_func(self):
        try:
            operator = Operator.objects.get(user_id=self.request.user.id)
            event = Event.objects.get(id=self.kwargs.get('pk'))
            return operator.is_check and operator.is_active and operator.department_id == event.location_id.department_id
        except Operator.DoesNotExist:
            return False


class EventsAll(UserPassesTestMixin, ListView):
    model = Event
    ordering = 'datetime'
    template_name = 'events_all.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = EventFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        try:
            context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
        except Coordinator.DoesNotExist:
            pass
        try:
            context['operator'] = Operator.objects.get(id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        return context

    def test_func(self):
        try:
            if self.request.user.staff == 'CO':
                try:
                    coordinator = Coordinator.objects.get(user_id=self.request.user.id)
                    return coordinator.is_check and coordinator.is_active
                except Coordinator.DoesNotExist:
                    return False
            elif self.request.user.staff == 'OP':
                try:
                    operator = Operator.objects.get(user_id=self.request.user.id)
                    return operator.is_check and operator.is_active
                except Operator.DoesNotExist:
                    return False
        except AttributeError:
            return False


