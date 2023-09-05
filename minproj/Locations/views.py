# from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import UserPassesTestMixin
# from django.http import HttpResponseRedirect
#
# from Minapp.models import Department, Location #  Recipient Operator, Coordinator,
# # from .forms import LocationForm, LocationUpdateForm
#
#
# @method_decorator(login_required(login_url='../login/'), name='dispatch')
# class Locations(ListView):
#     model = Location
#     ordering = 'id'
#     template_name = 'locations.html'
#     context_object_name = 'locations'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
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
#
#
#
# @method_decorator(login_required(login_url='../login/'), name='dispatch')
# class Detail(DetailView):
#     model = Location
#     template_name = 'location.html'
#     context_object_name = 'location'
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
# class PassRequestToFormViewMixin:  # Класс для добавления request-данных в форму создания локации
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['request'] = self.request
#         return kwargs
#
#
# class Create(UserPassesTestMixin, PassRequestToFormViewMixin, CreateView):
#     model = Location
#     form_class = LocationForm
#     template_name = 'location_update.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['operator'] = Operator.objects.get(id=self.request.user.id)
#         except Operator.DoesNotExist:
#             pass
#         return context
#
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             return operator.is_check and operator.is_active
#         except Operator.DoesNotExist:
#             return False
#
#
# class Update(UserPassesTestMixin, UpdateView):
#     model = Location
#     form_class = LocationUpdateForm
#     template_name = 'location_update.html'
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
#             location = Location.objects.get(id=self.kwargs.get('pk'))
#             return operator.is_check and operator.is_active and operator.department_id == location.department_id
#         except Operator.DoesNotExist:
#             return False
#
#
# class Delete(UserPassesTestMixin, DeleteView):
#     model = Location
#     template_name = 'location_delete.html'
#     context_object_name = 'location'
#     success_url = '/locations'
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
#             location = Location.objects.get(id=self.kwargs.get('pk'))
#             location.is_active = False
#             location.save()
#         except Location.DoesNotExist:
#             pass
#         return HttpResponseRedirect(success_url)
#
#     def test_func(self):
#         try:
#             operator = Operator.objects.get(user_id=self.request.user.id)
#             location = Location.objects.get(id=self.kwargs.get('pk'))
#             return operator.is_check and operator.is_active and operator.department_id == location.department_id
#         except Operator.DoesNotExist:
#             return False
