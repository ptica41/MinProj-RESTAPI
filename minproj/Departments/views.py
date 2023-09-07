from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import DepartmentSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Department, Location
from Locations.serializers import LocationSerializer


class DepartmentsAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.is_active and user.is_check:
            departments = Department.objects.all().order_by('id')
            serializer = DepartmentSerializer(instance=departments, many=True)
            return Response(user_response(True, "Departments were send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))



    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            department = request.data
            serializer = DepartmentSerializer(data=department)
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Department was create successful", 201, serializer.data),
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class DepartmentAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            department = Department.objects.get(id=kwargs.get('pk'))
            if user.is_active and user.is_check:
                serializer = DepartmentSerializer(instance=department)
                return Response(user_response(True, "Department was send successful", 200, serializer.data),
                                status=status.HTTP_200_OK)
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            department = Department.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = DepartmentSerializer(department, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Department was patch successful", 200, serializer.data),
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
            department = Department.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                department.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


class DepartmentLocationsAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            department = Department.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                locations = Location.objects.filter(department_id=department).order_by('id')
            elif user.staff == 'OP' and user.is_active and user.is_check:
                locations = Location.objects.exclude(~Q(department_id=user.department_id), is_active=False).filter(
                    department_id=department).order_by('id')
            elif user.is_active and user.is_check:
                locations = Location.objects.filter(department_id=department, is_active=True).order_by('id')
            else:
                raise serializers.ValidationError(
                    user_response(False, "Permission denied", 403, None, "ValidationError"))

            serializer = LocationSerializer(instance=locations, many=True)
            return Response(user_response(True, "Locations were send successful", 200, serializer.data),
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


