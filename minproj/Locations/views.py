# from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import UserPassesTestMixin
# from django.http import HttpResponseRedirect
#
# from Minapp.models import Department, Location #  Recipient Operator, Coordinator,
# # from .forms import LocationForm, LocationUpdateForm
#
#
# @method_decorator(login_required(login_url='../login/'), name='dispatch')
# class Locations(ListView):
#     model = Location
#     ordering = 'id'
#     template_name = 'locations.html'
#     context_object_name = 'locations'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         try:
#             context['recipient'] = Recipient.objects.get(id=self.request.user.id)
#         except Recipient.DoesNotExist:
#             pass
#         try:
#             context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
#         except Coordinator.DoesNotExist:
#             pass
#         return context
#
#
#
# @method_decorator(login_required(login_url='../login/'), name='dispatch')
# class Detail(DetailView):
#     model = Location
#     template_name = 'location.html'
#     context_object_name = 'location'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['recipient'] = Recipient.objects.get(id=self.request.user.id)
#         except Recipient.DoesNotExist:
#             pass
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
# class PassRequestToFormViewMixin:  # Класс для добавления request-данных в форму создания локации
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['request'] = self.request
#         return kwargs
#
#
# class Create(UserPassesTestMixin, PassRequestToFormViewMixin, CreateView):
#     model = Location
#     form_class = LocationForm
#     template_name = 'location_update.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             return operator.is_check and operator.is_active
#         except Operator.DoesNotExist:
#             return False
#
#
# class Update(UserPassesTestMixin, UpdateView):
#     model = Location
#     form_class = LocationUpdateForm
#     template_name = 'location_update.html'
#     success_url = '../'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             location = Location.objects.get(id=self.kwargs.get('pk'))
#             return operator.is_check and operator.is_active and operator.department_id == location.department_id
#         except Operator.DoesNotExist:
#             return False
#
#
# class Delete(UserPassesTestMixin, DeleteView):
#     model = Location
#     template_name = 'location_delete.html'
#     context_object_name = 'location'
#     success_url = '/locations'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#     def form_valid(self, form):
#         success_url = self.get_success_url()
#         try:
#             location = Location.objects.get(id=self.kwargs.get('pk'))
#             location.is_active = False
#             location.save()
#         except Location.DoesNotExist:
#             pass
#         return HttpResponseRedirect(success_url)
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             location = Location.objects.get(id=self.kwargs.get('pk'))
#             return operator.is_check and operator.is_active and operator.department_id == location.department_id
#         except Operator.DoesNotExist:
#             return False

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import LocationSerializer, LocationOperatorSerializer, AdminPatchLocationSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Department, Location


class LocationsAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            locations = Location.objects.all().order_by('id')
        elif user.staff == 'OP' and user.is_active and user.is_check:
            locations = Location.objects.exclude(~Q(department_id=user.department_id), is_active=False).order_by('id')
        elif user.is_active and user.is_check:
            locations = Location.objects.exclude(is_active=False).order_by('id')
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

        serializer = LocationSerializer(instance=locations, many=True)
        return Response(user_response(True, "Locations were send successful", 200, serializer.data),
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            location = request.data
            serializer = AdminPatchLocationSerializer(data=location)
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Location was create successful", 201, serializer.data),
                                status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(
                    False, "Incorrect data", 400, serializer.errors, exception="ValidationError"),
                    status=status.HTTP_400_BAD_REQUEST)
        elif user.staff == 'OP' and user.is_check and user.is_active:
            location = request.data
            serializer = LocationOperatorSerializer(data=location, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Location was create successful", 201, serializer.data),
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class LocationAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            location = Location.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = LocationSerializer(instance=location)
            elif (user.staff == 'CO' or user.staff == 'RE') and user.is_check and user.is_active and location.is_active:
                serializer = LocationSerializer(instance=location)
            elif user.staff == 'OP' and user.is_active and user.is_check:
                if location.is_active or (not location.is_active and location.department_id == user.department_id):
                    serializer = LocationSerializer(instance=location)
                else:
                    raise serializers.ValidationError(
                        user_response(False, "Permission denied", 403, None, "ValidationError"))
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "Location were send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            location = Location.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = AdminPatchLocationSerializer(location, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Location was patch successful", 200, serializer.data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                                  exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.staff == 'OP' and user.is_active and user.is_check and user.department_id == location.department_id:
                serializer = LocationOperatorSerializer(location, data=request.data, partial=True,
                                                        context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Location was patch successful", 200, serializer.data),
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
            location = Location.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                location.delete()
            elif user.staff == 'OP' and user.is_active and user.is_check and user.department_id == location.department_id:
                location.is_active = False
                location.save()
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))
