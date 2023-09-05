# from django.contrib.auth.forms import UserCreationForm
# from Minapp.models import User, Recipient
# from django import forms
#
# class RegisterForm(UserCreationForm):
#     def __init__(self, *args, **kwargs):
#         super(RegisterForm, self).__init__(*args, **kwargs)
#         self.fields['staff'].initial = 'RE'
#
#     staff = forms.CharField(widget=forms.HiddenInput())
#
#     class Meta:
#         model = User
#         fields = [
#             'username',
#             'name',
#             'surname',
#             'middle_name',
#             'phone',
#             'email',
#             'photo',
#             'staff'
#         ]
#
#
# class UpdateFormByRecipient(forms.ModelForm):
#
#     class Meta:
#         model = User
#         fields = ['username',
#                   'name',
#                   'surname',
#                   'middle_name',
#                   'phone',
#                   'email',
#                   'photo',
#                   ]
#
#
# class UpdateFormByCoordinator(forms.ModelForm):
#
#     class Meta:
#         model = Recipient
#         fields = ['is_check',
#                   'is_active']
