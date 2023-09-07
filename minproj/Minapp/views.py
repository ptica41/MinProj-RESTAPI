import datetime
import json

import pytz
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework import serializers, status

from django.conf import settings
from .models import User, Department, Location  # , Recipient, Coordinator, Operator,
from .serializers import LoginSerializer, UserSerializer, CreateUserSerializer, PatchUserAdminSerializer, \
    PatchRecipientCoordinatorSerializer
from .renderers import UserJSONRenderer


def get_user_dict(user):
    info = {}
    info['id'] = str(user.id)
    if user.last_login:
        info['last_login'] = str(user.last_login.astimezone(pytz.timezone(settings.TIME_ZONE)))
    if user.date_joined:
        info['date_joined'] = str(user.date_joined.astimezone(pytz.timezone(settings.TIME_ZONE)))
    if user.username:
        info['username'] = user.username
    if user.name:
        info['name'] = user.name
    if user.surname:
        info['surname'] = user.surname
    if user.middle_name:
        info['middle_name'] = user.middle_name
    if user.staff:
        info['staff'] = user.staff
    if user.phone:
        info['phone'] = str(user.phone)
    if user.email:
        info['email'] = str(user.email)
    if user.photo:
        info['photo'] = str(user.photo)
    if user.department_id:
        info['department_id'] = str(user.department_id)
    info['is_active'] = user.is_active
    info['is_check'] = user.is_check
    return info


def user_response(is_success: bool, message: str, http_code: int, data, exception=None):
    if exception:
        return {"isSuccess": is_success, "message": message, "httpCode": http_code, "data": data,
                "exception": exception}
    else:
        return {"isSuccess": is_success, "message": message, "httpCode": http_code, "data": data}
    # return Response(resp, status=http_code)


class BearerToken(TokenAuthentication):
    '''
    Переопределяем класс для использования в заголовке запроса Authorisation: Bearer вместо Authorisation: Token
    Также добавляем проверку на срок жизни токена и статуса is_active пользователя
    '''

    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        try:
            token = self.get_model().objects.get(key=key)
        except self.get_model().DoesNotExist:

            raise AuthenticationFailed(user_response(False, "Invalid token",
                                                     401, None, exception="AuthenticationFailed"))

        if not token.user.is_active:
            raise AuthenticationFailed(user_response(False, "User inactive or deleted", 401, None,
                                                     exception="AuthenticationFailed"))

        if token.created.timestamp() < (
                datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=30)).timestamp():
            raise AuthenticationFailed(user_response(False, "Token has expired", 401, None,
                                                     exception="AuthenticationFailed"))

        token.user.last_login = datetime.datetime.now(tz=timezone.utc)
        token.user.save()

        return token.user, token


class IsAuth(IsAuthenticated):
    def has_permission(self, request, view):
        status = bool(request.user and request.user.is_authenticated)
        if not status:
            raise serializers.ValidationError(user_response(False, "User is not authenticate",
                                                            401, None, exception="AuthenticationFailed"))
        return status


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            return Response(user_response(True, "User was send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)
        else:
            return Response(user_response(False, "User with this username and password was not found",
                                          400, None, exception="AuthenticationFailed"),
                            status=status.HTTP_400_BAD_REQUEST)

        # return Response(serializer.data, status=status.HTTP_200_OK)


class WhoAmIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    # renderer_classes = (UserJSONRenderer,)

    def get(self, request):
        user = request.user
        return Response(user_response(True, "User was send successful", 200, get_user_dict(user)),
                        status=status.HTTP_200_OK)


class UsersAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            users = User.objects.all().order_by('id')
        elif user.staff == 'CO' and user.is_active and user.is_check:
            users = User.objects.exclude(staff='AD').exclude(staff='CO', is_active=False).exclude(staff='CO',
                                                                                                  is_check=False).exclude(
                staff='OP', is_active=False).exclude(staff='OP', is_check=False).order_by('id')
        elif user.staff == 'OP' and user.is_active and user.is_check:
            users = User.objects.exclude(staff='AD').filter(is_active=True, is_check=True).order_by('id')
        elif user.staff == 'RE' and user.is_active and user.is_check:
            users = User.objects.filter(staff='CO', is_active=True, is_check=True).order_by('id')
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

        serializer = UserSerializer(instance=users, many=True)
        return Response(user_response(True, "Users were send successful", 200, serializer.data),
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            profile = request.data
            serializer = CreateUserSerializer(data=profile)
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "User was create successful", 201, serializer.data),
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class UserAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            profile = User.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = UserSerializer(instance=profile)
            elif user.staff == 'CO' and user.is_active and user.is_check:
                if profile.staff == 'RE' or (profile.staff == 'CO' and profile.is_active and profile.is_check) or (
                        profile.staff == 'OP' and profile.is_active and profile.is_check):
                    serializer = UserSerializer(instance=profile)
                else:
                    raise serializers.ValidationError(
                        user_response(False, "Permission denied", 403, None, "ValidationError"))
            elif user.staff == 'OP' and user.is_active and user.is_check:
                if profile.staff != 'AD' and profile.is_active and profile.is_check:
                    serializer = UserSerializer(instance=profile)
                else:
                    raise serializers.ValidationError(
                        user_response(False, "Permission denied", 403, None, "ValidationError"))
            elif user.staff == 'RE' and user.is_active and user.is_check:
                if profile.staff == 'CO' and profile.is_active and profile.is_check:
                    serializer = UserSerializer(instance=profile)
                else:
                    raise serializers.ValidationError(
                        user_response(False, "Permission denied", 403, None, "ValidationError"))
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "User were send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            profile = User.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = PatchUserAdminSerializer(profile, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "User was patch successful", 200, serializer.data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                                  exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user == profile and user.is_check and user.is_active:
                serializer = UserSerializer(profile, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "User was patch successful", 200, serializer.data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                                  exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.is_check and user.is_active and user.staff == 'CO' and profile.staff == 'RE':
                serializer = PatchRecipientCoordinatorSerializer(profile, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "User was patch successful", 200, serializer.data),
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
            profile = User.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                profile.delete()
            elif user == profile:
                profile.is_active = False
                profile.save()
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))



# class LogView(LoginView):
#
#     def get_success_url(self):
#         if self.request.user.staff == 'AD':
#             return '/admin'
#         elif self.request.user.staff == 'CO':
#             return f'/coordinators/{self.request.user.id}'
#         elif self.request.user.staff == 'OP':
#             return f'/operators/{self.request.user.id}'
#         elif self.request.user.staff == 'RE':
#             return f'/recipients/{self.request.user.id}'
#         else:
#             return '/'


# @method_decorator(login_required(login_url='../login/'), name='dispatch')
# class Departments(ListView):
#     model = Department
#     ordering = 'id'
#     template_name = 'departments.html'
#     context_object_name = 'departments'
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
#
# @method_decorator(login_required(login_url='../login/'), name='dispatch')
# class LocationsDepartment(ListView):
#     model = Location
#     ordering = 'id'
#     template_name = 'locations_department.html'
#     context_object_name = 'locations'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         try:
#             context['department'] = Department.objects.get(id=self.kwargs.get('pk'))
#         except Department.DoesNotExist:
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
