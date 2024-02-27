from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from communications.models import UserContactInfo


class SignUpForm(UserCreationForm):
    """
    Form for account creation
    """
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
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.username = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Create or update the UserContactInfo instance
            UserContactInfo.objects.update_or_create(
                user=user,
                defaults={'phone_number': self.cleaned_data.get('phone_number')}
            )
        return user
