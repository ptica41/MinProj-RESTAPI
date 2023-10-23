from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView

from .serializers import EventSerializer, CoordinatorEventSerializer, AdminEventSerializer
from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User, Event, UserGroups


class EventsAPIView(ListAPIView):

    serializer_class = EventSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    search_fields = ['name']
    ordering_fields = '__all__'
    filterset_fields = {
        "is_finished": ["exact", ],
        "is_check": ["exact", ],
        "datetime": ["lte", "gte"],
        "start": ["lte", "gte"],
        "end": ["lte", "gte"],
        "location_id_id": ["exact", ],
        "recipient_id_id": ["exact", ],
        "group_id_id": ["exact", ],
    }

    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD' or ((user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check):
            return Event.objects.all().order_by('datetime', 'start', 'end')
        elif user.staff == 'RE' and user.is_active and user.is_check:
            return Event.objects.filter(is_check=True, recipient_id=user_id).order_by('datetime', 'start', 'end') | Event.objects.filter(is_check=True, group_id__in=user.groups.values('id')).order_by('datetime', 'start', 'end')
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "Events were send successful", 200, response.data), status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #     user_id = Token.objects.get(key=token.split(' ')[1]).user_id
    #     user = User.objects.get(id=user_id)
    #
    #     if user.staff == 'AD' or ((user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check):
    #         events = Event.objects.all()
    #     elif user.staff == 'RE' and user.is_active and user.is_check:
    #         events = Event.objects.filter(is_check=True, recipient_id=user_id) | Event.objects.filter(is_check=True, group_id__in=user.groups.values('id'))
    #     else:
    #         raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
    #
    #     results = self.paginate_queryset(events, request, view=self)
    #     serializer = EventSerializer(instance=results, many=True)
    #     res_dict = {"count": self.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "results": serializer.data}
    #     return Response(user_response(True, "Events were send successful", 200, res_dict), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            event = request.data
            serializer = AdminEventSerializer(data=event, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Event was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(
                    user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
        elif user.staff == 'OP' and user.is_check and user.is_active:
            event = request.data
            serializer = EventSerializer(data=event, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(user_response(True, "Event was create successful", 201, serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(
                    user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))


class EventAPIView(APIView):
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)
        print(list(UserGroups.objects.filter(user_id=user.id).values('group_id')))

        try:
            event = Event.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD' or ((user.staff == 'OP' or user.staff == 'CO') and user.is_active and user.is_check):
                serializer = EventSerializer(instance=event)
            elif user.staff == 'RE' and user.is_active and user.is_check and event.is_check:
                try:
                    if event.recipient_id == user or {'group_id': event.group_id.id} in list(UserGroups.objects.filter(user_id=user.id).values('group_id')):
                        serializer = EventSerializer(instance=event)
                except AttributeError:
                    raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(user_response(True, "Event was send successful", 200, serializer.data), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))

    def patch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        try:
            event = Event.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD':
                serializer = AdminEventSerializer(event, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Event was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.staff == 'OP' and user.is_check and user.is_active and user.department_id == event.location_id.department_id:
                serializer = EventSerializer(event, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Event was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
                else:
                    return Response(user_response(False, "Incorrect data", 400, serializer.errors, exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)
            elif user.staff == 'CO' and user.is_active and user.is_check:
                serializer = CoordinatorEventSerializer(event, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(user_response(True, "Event was patch successful", 200, serializer.data), status=status.HTTP_200_OK)
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
            event = Event.objects.get(id=kwargs.get('pk'))
            if user.staff == 'AD' or (user.staff == 'OP' and user.is_check and user.is_active and user.department_id == event.location_id.department_id):
                event.delete()
            else:
                raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(user_response(False, "Wrong ID", 400, None, "ValidationError"))
