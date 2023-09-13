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

from .serializers import GroupSerializer, AdminGroupSerializer
from Minapp.serializers import UserSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Group, UserGroups


class GroupsAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            groups = Group.objects.all().order_by('id')
        elif (user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check:
            groups = Group.objects.filter(is_active=True).order_by('id')
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

        serializer = GroupSerializer(instance=groups, many=True)
        return Response(user_response(True, "Groups were send successful", 200, serializer.data),
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
            group = request.data
            serializer = GroupSerializer(data=group)
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Group was create successful", 201, serializer.data),
                                status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(
                    False, "Incorrect data", 400, serializer.errors, exception="ValidationError"),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class GroupAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = GroupSerializer(instance=group)
            elif (user.staff == 'CO' or user.staff == 'OP') and user.is_check and user.is_active and group.is_active:
                serializer = GroupSerializer(instance=group)
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "Group was send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = AdminGroupSerializer(group, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Group was patch successful", 200, serializer.data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                                  exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.staff == 'CO' and user.is_active and user.is_check and group.is_active:
                serializer = GroupSerializer(group, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Group was patch successful", 200, serializer.data),
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
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                group.delete()
            elif user.staff == 'CO' and user.is_active and user.is_check:
                group.is_active = False
                group.save()
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


class GroupUsersAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                users = User.objects.filter(groups=group).order_by('id')
            elif user.staff == 'CO' and user.is_active and user.is_check and group.is_active:
                users = User.objects.filter(groups=group).order_by('id')
            elif user.staff == 'OP' and user.is_active and user.is_check and group.is_active:
                users = User.objects.filter(groups=group, is_active=True, is_check=True)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserSerializer(instance=users, many=True)
            return Response(user_response(True, "Users were send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            user_id = request.data['id']
            recipient = User.objects.get(id=user_id)
            if recipient.staff != 'RE':
                raise serializers.ValidationError(user_response(False, "User isn't a Recipient", 400, None, "ValidationError"))
            if user.staff == 'AD':
                if not UserGroups.objects.filter(group_id=group.id, user_id=user_id).exists():
                    UserGroups.objects.create(group_id=group.id, user_id=user_id)
                    users = User.objects.filter(groups=group).order_by('id')
                else:
                    raise serializers.ValidationError(user_response(False, "Group with User already exists", 400, None, "ValidationError"))
            elif user.staff == 'CO' and user.is_check and user.is_active and group.is_active:
                if recipient.is_active and recipient.is_check and not UserGroups.objects.filter(group_id=group.id, user_id=user_id).exists():
                    UserGroups.objects.create(group_id=group.id, user_id=user_id)
                    users = User.objects.filter(groups=group, is_active=True, is_check=True).order_by('id')
                else:
                    raise serializers.ValidationError(user_response(False, "Group with User already exists", 400, None, "ValidationError"))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserSerializer(instance=users, many=True)
            return Response(user_response(True, "User was add to Group successful", 201, serializer.data),
                            status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def delete(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            recipient_id = request.data['id']
            recipient = User.objects.get(id=recipient_id)
            if recipient.staff != 'RE':
                raise serializers.ValidationError(user_response(False, "User isn't a Recipient", 400, None, "ValidationError"))
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active and group.is_active):
                user_group = UserGroups.objects.get(group_id=group.id, user_id=recipient_id)
                user_group.delete()
                users = User.objects.filter(groups=group).order_by('id')
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserSerializer(instance=users, many=True)
            return Response(user_response(True, "User was delete from Group successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))
