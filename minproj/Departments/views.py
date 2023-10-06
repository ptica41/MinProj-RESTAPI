from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination

from .serializers import DepartmentSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Department, Location
from Locations.serializers import LocationSerializer


class DepartmentsAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(instance=departments, many=True)
        return Response(user_response(True, "Departments were send successful", 200, serializer.data), status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):

        stat = bool(request.user and request.user.is_authenticated)
        if not stat:
            raise serializers.ValidationError(user_response(False, "User is not authenticate",
                                                            401, None, exception="AuthenticationFailed"))

        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            department = request.data
            serializer = DepartmentSerializer(data=department)
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Department was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
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
                return Response(user_response(True, "Department was send successful", 200, serializer.data), status=status.HTTP_200_OK)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

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
                    return Response(user_response(True, "Department was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
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
            department = Department.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                department.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))


class DepartmentLocationsAPIView(APIView, LimitOffsetPagination):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            department = Department.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                locations = Location.objects.filter(department_id=department)
            elif user.staff == 'OP' and user.is_active and user.is_check:
                locations = Location.objects.exclude(~Q(department_id=user.department_id), is_active=False).filter(department_id=department)
            elif user.is_active and user.is_check:
                locations = Location.objects.filter(department_id=department, is_active=True)
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

            results = self.paginate_queryset(locations, request, view=self)
            serializer = LocationSerializer(instance=results, many=True)
            res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
            return Response(user_response(True, "Locations were send successful", 200, res_dict), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

