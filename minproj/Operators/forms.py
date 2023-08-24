from django.db import models
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django import forms

from phonenumber_field.modelfields import PhoneNumberField

from Minapp.models import User, Department  #, Recipient, Location


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['staff'].initial = 'OP'

    department_id = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, label="Ведомство")
    staff = forms.CharField(widget=forms.HiddenInput())
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'surname',
            'middle_name',
            'phone',
            'email',
            'photo',
            'staff',
            'department_id'
        ]


class UpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['staff'].initial = 'OP'

    staff = forms.CharField(widget=forms.HiddenInput())
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'surname',
            'middle_name',
            'phone',
            'email',
            'photo',
            'staff'
        ]
