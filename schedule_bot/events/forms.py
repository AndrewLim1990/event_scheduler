from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from communications.models import UserContactInfo
from events.models import UserEvent


class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)  # Pop the event from kwargs and store it
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    whatsapp_phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=20,
        required=False,
        label="Phone Number"
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        print("HALLLOOOOO")
        user = super(RegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['first_name'] + ' ' + self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create or update the UserContactInfo instance
            UserContactInfo.objects.update_or_create(
                user=user,
                defaults={'whatsapp_phone_number': self.cleaned_data.get('whatsapp_phone_number')}
            )
            UserEvent.objects.update_or_create(
                user=user,
                event=self.event,
                defaults={
                    "is_host": False,
                    "is_required": True
                }
            )
        return user


class EventCreationForm(forms.Form):
    event_name = forms.CharField(label='Event Name', max_length=100)
    event_times = forms.CharField(
        widget=forms.Textarea,
        help_text='Enter proposed times as start-end pairs separated by commas.'
    )
