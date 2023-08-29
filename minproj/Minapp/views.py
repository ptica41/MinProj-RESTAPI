import datetime
import json

import pytz
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from django.conf import settings
from .models import Department, Operator, Location, Recipient, Coordinator
from .serializers import LoginSerializer
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
    return info


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
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        if token.created.timestamp() < (datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=30)).timestamp():
            raise AuthenticationFailed('Token has expired')

        # token.user.last_login = datetime.datetime.now(tz=timezone.utc)
        # token.user.save()

        return token.user, token


class LoginAPIView(APIView):
    permission_classes = (AllowAny, )
    renderer_classes = (UserJSONRenderer, )
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class WhoAmIView(APIView):
    authentication_classes = (BearerToken, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (UserJSONRenderer, )

    def get(self, request):
        user = request.user
        return Response(get_user_dict(user), status=status.HTTP_200_OK)

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


@method_decorator(login_required(login_url='../login/'), name='dispatch')
class Departments(ListView):
    model = Department
    ordering = 'id'
    template_name = 'departments.html'
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recipient'] = Recipient.objects.get(id=self.request.user.id)
        except Recipient.DoesNotExist:
            pass
        try:
            context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
        except Coordinator.DoesNotExist:
            pass
        try:
            context['operator'] = Operator.objects.get(id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        return context


@method_decorator(login_required(login_url='../login/'), name='dispatch')
class LocationsDepartment(ListView):
    model = Location
    ordering = 'id'
    template_name = 'locations_department.html'
    context_object_name = 'locations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['operator'] = Operator.objects.get(id=self.request.user.id)
        except Operator.DoesNotExist:
            pass
        try:
            context['department'] = Department.objects.get(id=self.kwargs.get('pk'))
        except Department.DoesNotExist:
            pass
        try:
            context['recipient'] = Recipient.objects.get(id=self.request.user.id)
        except Recipient.DoesNotExist:
            pass
        try:
            context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
        except Coordinator.DoesNotExist:
            pass
        return context


