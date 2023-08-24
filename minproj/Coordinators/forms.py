from django.contrib.auth.forms import UserCreationForm
from Minapp.models import User
from django import forms

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['staff'].initial = 'CO'

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


class UpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['staff'].initial = 'CO'

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