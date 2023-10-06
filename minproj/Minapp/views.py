import datetime
import uuid

import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage

from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView

from .models import User, UserGroups, Group, Event
from .serializers import LoginSerializer, UserSerializer, AdminUserSerializer, PatchRecipientCoordinatorSerializer, UserGroupSerializer
from Events.serializers import EventSerializer


def get_user_dict(user):
    info = {}
    info['id'] = str(user.id)
    if user.last_login:
        info['last_login'] = str(user.last_login.astimezone(pytz.timezone(settings.TIME_ZONE)))
    if user.date_joined:
        info['date_joined'] = str(user.date_joined.astimezone(pytz.timezone(settings.TIME_ZONE)))
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
    if user.groups:
        print(user.groups.values())
        info['groups'] = user.groups.values()
    info['is_active'] = user.is_active
    info['is_check'] = user.is_check
    return info


def user_response(is_success: bool, message: str, http_code: int, data, exception=None):
    if exception:
        return {"isSuccess": is_success, "message": message, "httpCode": http_code, "data": data,
                "exception": exception}
    else:
        return {"isSuccess": is_success, "message": message, "httpCode": http_code, "data": data}


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
        stat = bool(request.user and request.user.is_authenticated)
        if not stat:
            raise serializers.ValidationError(user_response(False, "User is not authenticate",
                                                            401, None, exception="AuthenticationFailed"))
        return stat


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            return Response(user_response(True, "User was send successful", 200, serializer.data), status=status.HTTP_200_OK)
        else:
            return Response(user_response(False, "User with this phone and password was not found", 400, None, exception="AuthenticationFailed"), status=status.HTTP_400_BAD_REQUEST)


class WhoAmIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request):
        user = request.user
        return Response(user_response(True, "User was send successful", 200, get_user_dict(user)), status=status.HTTP_200_OK)


class UploadPhoto(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            data_list = []
            files = request.FILES.getlist('my-attachment', None)
            for file in files:
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                default_storage.save(filename, file)
                url = request.build_absolute_uri('/')
                data = {
                    "name": filename,
                    "url": url[:-1] + default_storage.url(filename)
                }
                data_list.append(data)
            return Response(user_response(True, "Photo was upload successful", 201, data_list), status=status.HTTP_201_CREATED)
        except MultiValueDictKeyError:
            raise serializers.ValidationError(user_response(False, "File isn't upload", 403, None, "ValidationError"))


class GetPhoto(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)
        name = kwargs.get('str')
        url = request.build_absolute_uri('/')
        if user.staff == 'AD' or (user.is_active and user.is_check):
            return Response(user_response(True, "Photo was send successful", 200, url[:-1] + default_storage.url(name)), status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class UsersAPIView(ListAPIView):

    serializer_class = UserSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    search_fields = ['surname']
    ordering_fields = '__all__'
    filterset_fields = {
        "is_active": ["exact", ],
        "is_check": ["exact", ],
        "date_joined": ["lte", "gte"],
        "last_login": ["lte", "gte"]
    }


    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            return User.objects.all()
        elif user.staff == 'CO' and user.is_active and user.is_check:
            return User.objects.exclude(staff='AD').exclude(staff='CO', is_active=False).exclude(staff='CO', is_check=False).exclude(
                staff='OP', is_active=False).exclude(staff='OP', is_check=False)
        elif user.staff == 'OP' and user.is_active and user.is_check:
            return User.objects.exclude(staff='AD').filter(is_active=True, is_check=True)
        elif user.staff == 'RE' and user.is_active and user.is_check:
            return User.objects.filter(staff='CO', is_active=True, is_check=True)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Users were send successful", 200, response.data), status=status.HTTP_200_OK)


    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD':
    #         self.queryset = User.objects.all()
    #     elif user.staff == 'CO' and user.is_active and user.is_check:
    #         self.queryset = User.objects.exclude(staff='AD').exclude(staff='CO', is_active=False).exclude(staff='CO', is_check=False).exclude(
    #             staff='OP', is_active=False).exclude(staff='OP', is_check=False)
    #     elif user.staff == 'OP' and user.is_active and user.is_check:
    #         self.queryset = User.objects.exclude(staff='AD').filter(is_active=True, is_check=True)
    #     elif user.staff == 'RE' and user.is_active and user.is_check:
    #         self.queryset = User.objects.filter(staff='CO', is_active=True, is_check=True)
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     # results = self.paginate_queryset(users)
    #     serializer = UserSerializer(instance=self.queryset, many=True)
    #     return Response(user_response(True, "Users were send successful", 200, serializer.data), status=status.HTTP_200_OK)
    #     return self.get_paginated_response(serializer.data)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}


    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            profile = request.data
            serializer = AdminUserSerializer(data=profile, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "User was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
        elif (user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check:
            profile = request.data
            serializer = AdminUserSerializer(data=profile, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "User was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
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
                if profile.staff == 'RE' or (profile.staff == 'CO' and profile.is_active and profile.is_check) or (profile.staff == 'OP' and profile.is_active and profile.is_check):
                    serializer = UserSerializer(instance=profile)
                else:
                    raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            elif user.staff == 'OP' and user.is_active and user.is_check:
                if profile.staff != 'AD' and profile.is_active and profile.is_check:
                    serializer = UserSerializer(instance=profile)
                else:
                    raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            elif user.staff == 'RE' and user.is_active and user.is_check:
                if (profile.staff == 'CO' or profile == user) and profile.is_active and profile.is_check:
                    serializer = UserSerializer(instance=profile)
                else:
                    raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "User were send successful", 200, serializer.data), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            profile = User.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = AdminUserSerializer(profile, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "User was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user == profile and user.is_check and user.is_active:
                serializer = UserSerializer(profile, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "User was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.is_check and user.is_active and user.staff == 'CO' and profile.staff == 'RE':
                serializer = PatchRecipientCoordinatorSerializer(profile, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "User was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

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
            elif user == profile and user.is_active and user.is_check:
                profile.is_active = False
                profile.save()
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


class CoordinatorsAPIView(ListAPIView):

    serializer_class = UserSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    search_fields = ['surname']
    ordering_fields = '__all__'
    filterset_fields = {
        "is_active": ["exact", ],
        "is_check": ["exact", ],
        "date_joined": ["lte", "gte"],
        "last_login": ["lte", "gte"]
    }

    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            return User.objects.filter(staff='CO')
        elif user.staff == 'CO' and user.is_active and user.is_check:
            return User.objects.filter(staff='CO', is_active=True, is_check=True)
        elif user.staff == 'OP' and user.is_active and user.is_check:
            return User.objects.filter(staff='CO', is_active=True, is_check=True)
        elif user.staff == 'RE' and user.is_active and user.is_check:
            return User.objects.filter(staff='CO', is_active=True, is_check=True)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Users were send successful", 200, response.data), status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD':
    #         users = User.objects.filter(staff='CO')
    #     elif user.staff == 'CO' and user.is_active and user.is_check:
    #         users = User.objects.filter(staff='CO', is_active=True, is_check=True)
    #     elif user.staff == 'OP' and user.is_active and user.is_check:
    #         users = User.objects.filter(staff='CO', is_active=True, is_check=True)
    #     elif user.staff == 'RE' and user.is_active and user.is_check:
    #         users = User.objects.filter(staff='CO', is_active=True, is_check=True)
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     results = self.paginate_queryset(users, request, view=self)
    #     serializer = UserSerializer(instance=results, many=True)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
    #     return Response(user_response(True, "Users were send successful", 200, res_dict), status=status.HTTP_200_OK)


class OperatorsAPIView(ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    search_fields = ['surname']
    ordering_fields = '__all__'
    filterset_fields = {
        "is_active": ["exact", ],
        "is_check": ["exact", ],
        "date_joined": ["lte", "gte"],
        "last_login": ["lte", "gte"]
    }

    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            return User.objects.filter(staff='OP')
        elif user.staff == 'CO' and user.is_active and user.is_check:
            return User.objects.filter(staff='OP', is_active=True, is_check=True)
        elif user.staff == 'OP' and user.is_active and user.is_check:
            return User.objects.filter(staff='OP', is_active=True, is_check=True)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Users were send successful", 200, response.data), status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD':
    #         users = User.objects.filter(staff='OP')
    #     elif (user.staff == 'CO' or user.staff == 'OP') and user.is_active and user.is_check:
    #         users = User.objects.filter(staff='OP', is_active=True, is_check=True)
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     results = self.paginate_queryset(users, request, view=self)
    #     serializer = UserSerializer(instance=results, many=True)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
    #     return Response(user_response(True, "Users were send successful", 200, res_dict), status=status.HTTP_200_OK)


class RecipientsAPIView(ListAPIView):

    serializer_class = UserSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    search_fields = ['surname']
    ordering_fields = '__all__'
    filterset_fields = {
        "is_active": ["exact", ],
        "is_check": ["exact", ],
        "date_joined": ["lte", "gte"],
        "last_login": ["lte", "gte"]
    }

    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            return User.objects.filter(staff='RE')
        elif user.staff == 'CO' and user.is_active and user.is_check:
            return User.objects.filter(staff='RE')
        elif user.staff == 'OP' and user.is_active and user.is_check:
            return User.objects.filter(staff='RE', is_active=True, is_check=True)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Users were send successful", 200, response.data), status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD' or (user.staff == 'CO' and user.is_active and user.is_check):
    #         users = User.objects.filter(staff='RE')
    #     elif user.staff == 'OP' and user.is_active and user.is_check:
    #         users = User.objects.filter(staff='RE', is_active=True, is_check=True)
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     results = self.paginate_queryset(users, request, view=self)
    #     serializer = UserSerializer(instance=results, many=True)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
    #     return Response(user_response(True, "Users were send successful", 200, res_dict), status=status.HTTP_200_OK)


class UserGroupsAPIView(APIView, LimitOffsetPagination):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            recipient = User.objects.get(id=kwargs.get('pk'))
            if recipient.staff != 'RE':
                raise serializers.ValidationError(user_response(False, "User isn't a Recipient", 400, None, "ValidationError"))
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_active and user.is_check):
                groups = UserGroups.objects.filter(user_id=recipient.id)
            elif user.staff == 'OP' and user.is_active and user.is_check and recipient.is_active and recipient.is_check:
                groups = UserGroups.objects.filter(user_id=recipient.id, group_id__is_active=True)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            results = self.paginate_queryset(groups, request, view=self)
            serializer = UserGroupSerializer(instance=results, many=True)
            res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
            return Response(user_response(True, "Groups were send successful", 200, res_dict), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            recipient = User.objects.get(id=kwargs.get('pk'))
            group_id = request.data['id']
            if not Group.objects.filter(id=group_id).exists():
                raise serializers.ValidationError(user_response(False, "Group isn't exist", 400, None, "ValidationError"))
            if recipient.staff != 'RE':
                raise serializers.ValidationError(user_response(False, "User isn't a Recipient", 400, None, "ValidationError"))
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
                if not UserGroups.objects.filter(group_id=group_id, user_id=recipient.id).exists():
                    UserGroups.objects.create(group_id=group_id, user_id=recipient.id)
                    groups = UserGroups.objects.filter(user_id=recipient.id)
                else:
                    raise serializers.ValidationError(user_response(False, "User in group already exists", 400, None, "ValidationError"))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserGroupSerializer(instance=groups, many=True)
            return Response(user_response(True, "User was add to Group successful", 201, serializer.data), status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def delete(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            recipient = User.objects.get(id=kwargs.get('pk'))
            group_id = request.data['id']
            if not Group.objects.filter(id=group_id).exists():
                raise serializers.ValidationError(user_response(False, "Group isn't exist", 400, None, "ValidationError"))
            if recipient.staff != 'RE':
                raise serializers.ValidationError(user_response(False, "User isn't a Recipient", 400, None, "ValidationError"))
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
                user_group = UserGroups.objects.get(group_id=group_id, user_id=recipient.id)
                user_group.delete()
                groups = UserGroups.objects.filter(user_id=recipient.id)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserGroupSerializer(instance=groups, many=True)
            return Response(user_response(True, "User was delete from Group successful", 200, serializer.data), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


class UserEventsAPIView(APIView, LimitOffsetPagination):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            recipient = User.objects.get(id=kwargs.get('pk'))
            if recipient.staff != 'RE':
                raise serializers.ValidationError(user_response(False, "User isn't a Recipient", 400, None, "ValidationError"))
            if user.staff == 'AD' or ((user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check):
                events = Event.objects.filter(recipient_id=recipient.id) | Event.objects.filter(group_id__in=recipient.groups.values('id'))
            elif user.staff == 'RE' and user.is_active and user.is_check and user == recipient:
                events = Event.objects.filter(is_check=True, recipient_id=recipient.id) | Event.objects.filter(is_check=True, group_id__in=recipient.groups.values('id'))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            results = self.paginate_queryset(events, request, view=self)
            serializer = EventSerializer(instance=results, many=True)
            res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
            return Response(user_response(True, "Events were send successful", 200, res_dict), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))
