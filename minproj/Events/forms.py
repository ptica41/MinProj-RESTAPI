from django import forms

from Minapp.models import Event, Location, Recipient, Operator


class EventForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.operator = Operator.objects.get(user_id=request.user.id)
        self.fields['location_id'].queryset = Location.objects.filter(department_id=self.operator.department_id, is_active=True)
        self.fields['recipient_id'].queryset = Recipient.objects.filter(is_check=True, is_active=True)



    class Meta:
        model = Event
        fields = ['name',
                  'description',
                  'datetime',
                  'photo',
                  'location_id',
                  'recipient_id']


class EventUpdateForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super(EventUpdateForm, self).__init__(*args, **kwargs)
        self.operator = Operator.objects.get(user_id=request.user.id)
        self.fields['location_id'].queryset = Location.objects.filter(department_id=self.operator.department_id, is_active=True)
        self.fields['recipient_id'].queryset = Recipient.objects.filter(is_active=True, is_check=True)
        self.fields['is_check'].widget = forms.HiddenInput()
        if not self.instance.is_check:
            self.fields['is_finished'] = forms.BooleanField(disabled=True, required=False, label='Выполнено')


    class Meta:
        model = Event
        fields = ['name',
                  'description',
                  'datetime',
                  'photo',
                  'location_id',
                  'recipient_id',
                  'is_check',
                  'is_finished']


class EventUpdateFormByCoordinator(forms.ModelForm):

    class Meta:
        model = Recipient
        fields = ['is_check']
