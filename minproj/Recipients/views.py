from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer
from .renderers import UserJSONRenderer

from Minapp.models import User, Coordinator, Operator, Recipient, Department, Location, Event
from .forms import RegisterForm, UpdateFormByRecipient, UpdateFormByCoordinator


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# class Wait(TemplateView):
#     template_name = 'wait.html'


# class Register(CreateView):
#     model = User
#     form_class = RegisterForm
#     success_url = '../wait'

class Detail(UserPassesTestMixin, DetailView):
    model = User
    template_name = 'recipient.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recipient'] = Recipient.objects.get(id=self.request.user.id)
        except Recipient.DoesNotExist:
            pass
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
            elif self.request.user.staff == 'RE':
                try:
                    recipient = Recipient.objects.get(user_id=self.request.user.id)
                    return recipient.is_check and recipient.is_active and recipient.id == self.kwargs.get('pk')
                except Operator.DoesNotExist:
                    return False
        except AttributeError:
            return False


class UpdateByRecipient(UserPassesTestMixin, UpdateView):
    model = User
    form_class = UpdateFormByRecipient
    template_name = 'recipient_update.html'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recipient'] = Recipient.objects.get(id=self.request.user.id)
        except Recipient.DoesNotExist:
            pass
        return context

    def test_func(self):
        try:
            recipient = Recipient.objects.get(user_id=self.request.user.id)
            return recipient.is_check and recipient.is_active and self.request.user.id == self.kwargs.get('pk')
        except Recipient.DoesNotExist:
            return False


class UpdateByCoordinator(UserPassesTestMixin, UpdateView):
    model = Recipient
    form_class = UpdateFormByCoordinator
    template_name = 'recipient_edit.html'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recipient'] = User.objects.get(id=self.kwargs.get('pk'))
        except User.DoesNotExist:
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
    model = User
    template_name = 'recipient_delete.html'
    success_url = '/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recipient'] = Recipient.objects.get(id=self.request.user.id)
        except Recipient.DoesNotExist:
            pass
        return context

    def form_valid(self, form):
        success_url = self.get_success_url()
        try:
            recipient = Recipient.objects.get(user_id=self.object.id)
            recipient.is_active = False
            recipient.save()
        except Recipient.DoesNotExist:
            pass
        return HttpResponseRedirect(success_url)

    def test_func(self):
        try:
            recipient = Recipient.objects.get(user_id=self.request.user.id)
            return recipient.is_check and recipient.is_active and self.request.user.id == self.kwargs.get('pk')
        except Recipient.DoesNotExist:
            return False


class Recipients(UserPassesTestMixin, ListView):
    model = Recipient
    ordering = 'id'
    template_name = 'recipients.html'
    context_object_name = 'recipients'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class EventsToRecipient(UserPassesTestMixin, ListView):
    model = Event
    ordering = 'datetime'
    template_name = 'events_recipient.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recipient'] = Recipient.objects.get(id=self.kwargs.get('pk'))
        except Recipient.DoesNotExist:
            pass
        try:
            context['events'] = Event.objects.filter(recipient_id=context['recipient'].id).order_by('datetime')
        except Event.DoesNotExist:
            pass
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
            elif self.request.user.staff == 'RE':
                try:
                    recipient = Recipient.objects.get(user_id=self.request.user.id)
                    return recipient.is_check and recipient.is_active and self.request.user.id == self.kwargs.get('pk')
                except Operator.DoesNotExist:
                    return False
        except AttributeError:
            return False
