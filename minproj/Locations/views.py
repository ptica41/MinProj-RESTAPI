from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView

from .serializers import LocationSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Location


class LocationsAPIView(ListAPIView):

    serializer_class = LocationSerializer
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

        if user.staff == 'AD':
            return Location.objects.all()
        elif user.staff == 'OP' and user.is_active and user.is_check:
            return Location.objects.exclude(~Q(department_id=user.department_id), is_active=False)
        elif user.is_active and user.is_check:
            return Location.objects.exclude(is_active=False)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Locations were send successful", 200, response.data), status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD':
    #         locations = Location.objects.all()
    #     elif user.staff == 'OP' and user.is_active and user.is_check:
    #         locations = Location.objects.exclude(~Q(department_id=user.department_id), is_active=False)
    #     elif user.is_active and user.is_check:
    #         locations = Location.objects.exclude(is_active=False)
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     results = self.paginate_queryset(locations, request, view=self)
    #     serializer = LocationSerializer(instance=results, many=True)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
    #     return Response(user_response(True, "Locations were send successful", 200, res_dict), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            location = request.data
            serializer = LocationSerializer(data=location, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Location was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
        elif user.staff == 'OP' and user.is_check and user.is_active:
            location = request.data
            serializer = LocationSerializer(data=location, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Location was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
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
                    raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "Location was send successful", 200, serializer.data), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            location = Location.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = LocationSerializer(location, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Location was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.staff == 'OP' and user.is_active and user.is_check and user.department_id == location.department_id:
                serializer = LocationSerializer(location, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Location was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
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
            location = Location.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                location.delete()
            elif user.staff == 'OP' and user.is_active and user.is_check and user.department_id == location.department_id:
                location.is_active = False
                location.save()
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))
