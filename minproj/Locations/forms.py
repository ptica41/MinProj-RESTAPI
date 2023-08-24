from django import forms
from Minapp.models import Location, Operator, Department


class LocationForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        operator = Operator.objects.get(user_id=request.user.id)
        self.fields['department_id'].initial = operator.department_id_id
        self.fields['department_id'].widget = forms.HiddenInput()


    class Meta:
        model = Location
        fields = ['name',
                  'address',
                  'lat',
                  'lon',
                  'phone',
                  'email',
                  'photo',
                  'department_id']


class LocationUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationUpdateForm, self).__init__(*args, **kwargs)
        if self.instance.is_active:
            self.fields['is_active'] = forms.BooleanField(disabled=True, required=False, label="Активно")

    class Meta:
        model = Location
        fields = ['name',
                  'address',
                  'lat',
                  'lon',
                  'phone',
                  'email',
                  'photo',
                  'is_active']
