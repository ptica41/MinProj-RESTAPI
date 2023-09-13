# import datetime
#
# from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import UserPassesTestMixin
# from django.http import HttpResponseRedirect
#
# from Minapp.models import Event, Operator, Recipient, Coordinator
# from .forms import EventForm, EventUpdateForm, EventUpdateFormByCoordinator
# from .filters import EventFilter
#
#
# class PassRequestToFormViewMixin:  # Класс для добавления request-данных в форму создания локации
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['request'] = self.request
#         return kwargs
#
#
# class Create(UserPassesTestMixin, PassRequestToFormViewMixin, CreateView):
#     model = Event
#     form_class = EventForm
#     template_name = 'event_update.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(user_id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             return operator.is_check and operator.is_active
#         except Operator.DoesNotExist:
#             return False
#
#
# class Detail(UserPassesTestMixin, DetailView):
#     model = Event
#     template_name = 'event.html'
#     context_object_name = 'event'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
#         except Coordinator.DoesNotExist:
#             pass
#         try:
#             context['operator'] = Operator.objects.get(user_id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         try:
#             context['recipient'] = Recipient.objects.get(id=self.request.user.id)
#         except Recipient.DoesNotExist:
#             pass
#         return context
#
#     def test_func(self):
#         try:
#             if self.request.user.staff == 'CO':
#                 try:
#                     coordinator = Coordinator.objects.get(user_id=self.request.user.id)
#                     return coordinator.is_check and coordinator.is_active
#                 except Coordinator.DoesNotExist:
#                     return False
#             elif self.request.user.staff == 'OP':
#                 try:
#                     operator = Operator.objects.get(user_id=self.request.user.id)
#                     return operator.is_check and operator.is_active
#                 except Operator.DoesNotExist:
#                     return False
#             elif self.request.user.staff == 'RE':
#                 try:
#                     recipient = Recipient.objects.get(user_id=self.request.user.id)
#                     event = Event.objects.get(id=self.kwargs.get('pk'))
#                     return recipient.is_check and recipient.is_active and recipient == event.recipient_id
#                 except Operator.DoesNotExist:
#                     return False
#         except AttributeError:
#             return False
#
#
# class Update(UserPassesTestMixin, PassRequestToFormViewMixin, UpdateView):
#     model = Event
#     form_class = EventUpdateForm
#     template_name = 'event_update.html'
#     success_url = '../'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(user_id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             event = Event.objects.get(id=self.kwargs.get('pk'))
#             return operator.is_check and operator.is_active and operator.department_id == event.location_id.department_id
#         except Operator.DoesNotExist:
#             return False
#
#
# class UpdateByCoordinator(UserPassesTestMixin, UpdateView):
#     model = Event
#     form_class = EventUpdateFormByCoordinator
#     template_name = 'event_edit.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['event'] = Event.objects.get(id=self.kwargs.get('pk'))
#         except Event.DoesNotExist:
#             pass
#         try:
#             context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
#         except Coordinator.DoesNotExist:
#             pass
#         return context
#
#     def test_func(self):
#         try:
#             coordinator = Coordinator.objects.get(user_id=self.request.user.id)
#             return coordinator.is_check and coordinator.is_active
#         except Coordinator.DoesNotExist:
#             return False
#
#
# class Delete(UserPassesTestMixin, DeleteView):
#     model = Event
#     template_name = 'event_delete.html'
#     context_object_name = 'event'
#     success_url = '/events'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(user_id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             event = Event.objects.get(id=self.kwargs.get('pk'))
#             return operator.is_check and operator.is_active and operator.department_id == event.location_id.department_id
#         except Operator.DoesNotExist:
#             return False
#
#
# class EventsAll(UserPassesTestMixin, ListView):
#     model = Event
#     ordering = 'datetime'
#     template_name = 'events_all.html'
#     context_object_name = 'events'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         self.filterset = EventFilter(self.request.GET, queryset)
#         return self.filterset.qs
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['filterset'] = self.filterset
#         try:
#             context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
#         except Coordinator.DoesNotExist:
#             pass
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#     def test_func(self):
#         try:
#             if self.request.user.staff == 'CO':
#                 try:
#                     coordinator = Coordinator.objects.get(user_id=self.request.user.id)
#                     return coordinator.is_check and coordinator.is_active
#                 except Coordinator.DoesNotExist:
#                     return False
#             elif self.request.user.staff == 'OP':
#                 try:
#                     operator = Operator.objects.get(user_id=self.request.user.id)
#                     return operator.is_check and operator.is_active
#                 except Operator.DoesNotExist:
#                     return False
#         except AttributeError:
#             return False
#
#


from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import EventSerializer, CoordinatorEventSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Event


class EventsAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD' or ((user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check):
            events = Event.objects.all().order_by('id')
        elif user.staff == 'RE' and user.is_active and user.is_check:
            events = Event.objects.filter(is_check=True, recipient_id=user_id) | Event.objects.filter(is_check=True, group_id__in=user.groups.values('id'))
            events.order_by('id')
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

        serializer = EventSerializer(instance=events, many=True)
        return Response(user_response(True, "Events were send successful", 200, serializer.data),
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD' or (user.staff == 'OP' and user.is_check and user.is_active):
            event = request.data
            serializer = EventSerializer(data=event, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Event was create successful", 201, serializer.data),
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class EventAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            event = Event.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD' or ((user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check):
                serializer = EventSerializer(instance=event)
            elif user.staff == 'RE' and user.is_active and user.is_check and event.is_check and (event.recipient_id == user or event.group_id in user.groups):
                serializer = EventSerializer(instance=event)
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "Event was send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            event = Event.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD' or (user.staff == 'OP' and user.is_check and user.is_active):
                serializer = EventSerializer(event, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Event was patch successful", 200, serializer.data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                                  exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.staff == 'CO' and user.is_active and user.is_check:
                serializer = CoordinatorEventSerializer(event, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Event was patch successful", 200, serializer.data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                                  exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def delete(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            event = Event.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD' or (user.staff == 'OP' and user.is_check and user.is_active and user.department_id == event.location_id.department_id):
                event.delete()
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))