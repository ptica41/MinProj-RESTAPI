from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView

from .serializers import GroupSerializer
from Minapp.serializers import UserSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Group, UserGroups


class GroupsAPIView(ListAPIView):

    serializer_class = GroupSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    search_fields = ['name']
    ordering_fields = '__all__'
    filterset_fields = {
        "is_active": ["exact", ]
    }

    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD' or (user.staff == 'CO' and user.is_active and user.is_check):
            return Group.objects.all()
        elif user.staff == 'OP' and user.is_active and user.is_check:
            return Group.objects.filter(is_active=True)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Groups were send successful", 200, response.data), status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD' or (user.staff == 'CO' and user.is_active and user.is_check):
    #         groups = Group.objects.all()
    #     elif user.staff == 'OP' and user.is_active and user.is_check:
    #         groups = Group.objects.filter(is_active=True)
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     results = self.paginate_queryset(groups, request, view=self)
    #     serializer = GroupSerializer(instance=results, many=True)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
    #     return Response(user_response(True, "Groups were send successful", 200, res_dict), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
            group = request.data
            serializer = GroupSerializer(data=group)
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Group was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
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
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
                serializer = GroupSerializer(instance=group)
            elif user.staff == 'OP' and user.is_check and user.is_active and group.is_active:
                serializer = GroupSerializer(instance=group)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "Group was send successful", 200, serializer.data), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_active and user.is_check):
                serializer = GroupSerializer(group, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Group was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
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
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                group.delete()
            elif user.staff == 'CO' and user.is_active and user.is_check:
                group.is_active = False
                group.save()
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


class GroupUsersAPIView(APIView, LimitOffsetPagination):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            group = Group.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                users = User.objects.filter(groups=group)
            elif user.staff == 'CO' and user.is_active and user.is_check:
                users = User.objects.filter(groups=group)
            elif user.staff == 'OP' and user.is_active and user.is_check and group.is_active:
                users = User.objects.filter(groups=group, is_active=True, is_check=True)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            results = self.paginate_queryset(users, request, view=self)
            serializer = UserSerializer(instance=results, many=True)
            res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
            return Response(user_response(True, "Users were send successful", 200, res_dict), status=status.HTTP_200_OK)

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
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
                if not UserGroups.objects.filter(group_id=group.id, user_id=user_id).exists():
                    UserGroups.objects.create(group_id=group.id, user_id=user_id)
                    users = User.objects.filter(groups=group)
                else:
                    raise serializers.ValidationError(user_response(False, "Group with User already exists", 400, None, "ValidationError"))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserSerializer(instance=users, many=True)
            return Response(user_response(True, "User was add to Group successful", 201, serializer.data), status=status.HTTP_201_CREATED)

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
            if user.staff == 'AD' or (user.staff == 'CO' and user.is_check and user.is_active):
                user_group = UserGroups.objects.get(group_id=group.id, user_id=recipient_id)
                user_group.delete()
                users = User.objects.filter(groups=group)
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = UserSerializer(instance=users, many=True)
            return Response(user_response(True, "User was delete from Group successful", 200, serializer.data), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))
