from django import forms
from accounts.models import Member
from django.core.validators import RegexValidator
from communications.models import UserContactInfo
from events.models import UserEvent


class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)  # Pop the event from kwargs and store it
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=20,
        required=False,
        label="Phone Number"
    )

    class Meta:
        model = Member
        fields = ('first_name', 'last_name')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['phone_number']
        if commit:
            user_exists = Member.objects.filter(username=user.username).exists()
            if not user_exists:
                if user.email == "":
                    user.email = None
                user.save()
            else:
                user = Member.objects.get(username=self.cleaned_data['phone_number'])
                user.save()

            # Create or update the UserContactInfo instance
            UserContactInfo.objects.update_or_create(
                user=user,
                defaults={'phone_number': self.cleaned_data.get('phone_number')}
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
    event_times = forms.DateTimeField(
        widget=forms.HiddenInput(attrs={'class': 'hidden-date-input', 'placeholder': 'Select event date'})
    )
    event_duration = forms.IntegerField(
        label='Event Duration (minutes)',
        min_value=1,
        help_text='Duration in minutes.'
    )