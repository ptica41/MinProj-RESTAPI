from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import ListView

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Department, Operator, Location, Recipient, Coordinator
from .serializers import LoginSerializer
from .renderers import UserJSONRenderer


class LoginAPIView(APIView):
    permission_classes = (AllowAny, )
    renderer_classes = (UserJSONRenderer, )
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

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


