from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer
from .renderers import UserJSONRenderer

from Minapp.models import User, Department, Location, Event  #Coordinator, Operator, Recipient,
from .forms import RegisterForm, UpdateForm


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class Detail(UserPassesTestMixin, DetailView):
#     model = User
#     template_name = 'operator.html'
#     context_object_name = 'user'
#     is_signin = True
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             department_id = User.objects.get(id=self.kwargs.get('pk')).department_id_id
#             context['department'] = Department.objects.get(id=department_id)
#         except Department.DoesNotExist:
#             pass
#         try:
#             context['coordinator'] = Coordinator.objects.get(id=self.request.user.id)
#         except Coordinator.DoesNotExist:
#             pass
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         context['is_it'] = self.request.user.id == self.kwargs.get('pk')
#         return context
#
#     def handle_no_permission(self):
#         if self.is_signin == False:
#             return redirect('../../login')
#         return redirect('wait')
#
#     def test_func(self):
#         try:
#             if self.request.user.staff == 'CO':
#                 try:
#                     coordinator = Coordinator.objects.get(user_id=self.request.user.id)
#                     return coordinator.is_check and coordinator.is_active
#                 except Coordinator.DoesNotExist:
#                     self.is_signin = False
#                     return False
#             elif self.request.user.staff == 'OP':
#                 try:
#                     operator = Operator.objects.get(user_id=self.request.user.id)
#                     return operator.is_check and operator.is_active
#                 except Operator.DoesNotExist:
#                     self.is_signin = False
#                     return False
#         except AttributeError:
#             self.is_signin = False
#             return False
#
#
# class Update(UserPassesTestMixin, UpdateView):
#     model = User
#     form_class = UpdateForm
#     template_name = 'operator_update.html'
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
#             return operator.is_check and operator.is_active and self.request.user.id == self.kwargs.get('pk')
#         except Operator.DoesNotExist:
#             return False
#
#
# class Delete(UserPassesTestMixin, DeleteView):
#     model = User
#     template_name = 'operator_delete.html'
#     success_url = '/login'
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
#             operator = Operator.objects.get(user_id=self.object.id)
#             operator.is_active = False
#             operator.save()
#         except Operator.DoesNotExist:
#             pass
#         return HttpResponseRedirect(success_url)
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             return operator.is_check and operator.is_active and self.request.user.id == self.kwargs.get('pk')
#         except Operator.DoesNotExist:
#             return False
#
#
# class Operators(UserPassesTestMixin, ListView):
#     model = Operator
#     ordering = 'id'
#     template_name = 'operators.html'
#     context_object_name = 'operators'
#     is_signin = True
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
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
#     def handle_no_permission(self):
#         if not self.is_signin:
#             return redirect('../../login')
#         return redirect('wait')
#
#     def test_func(self):
#         try:
#             if self.request.user.staff == 'CO':
#                 try:
#                     coordinator = Coordinator.objects.get(user_id=self.request.user.id)
#                     return coordinator.is_check and coordinator.is_active
#                 except Coordinator.DoesNotExist:
#                     self.is_signin = False
#                     return False
#             elif self.request.user.staff == 'OP':
#                 try:
#                     operator = Operator.objects.get(user_id=self.request.user.id)
#                     return operator.is_check and operator.is_active
#                 except Operator.DoesNotExist:
#                     self.is_signin = False
#                     return False
#         except AttributeError:
#             self.is_signin = False
#             return False
