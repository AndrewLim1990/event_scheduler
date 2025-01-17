from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Member
from django.core.validators import RegexValidator
from communications.models import UserContactInfo
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


def validate_account_exists(phone_number):
    phone_number_exists = UserContactInfo.objects.filter(phone_number=phone_number).exists()
    # Check if account exists with phone number and password
    if phone_number_exists:
        has_password = UserContactInfo.objects.get(phone_number=phone_number).user.password != ""
        if has_password:
            raise ValidationError('An account with that phone number already has an account. Please log in.')


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))


class SignUpForm(UserCreationForm):
    """
    Form for account creation
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = forms.CharField(
        validators=[phone_regex, validate_account_exists],
        max_length=20,
        required=True,
        label="Phone Number"
    )

    class Meta:
        model = Member
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
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        phone_number = self.cleaned_data.get('phone_number')

        if commit:
            user_exists = UserContactInfo.objects.filter(phone_number=phone_number).exists()
            if user_exists:
                user = UserContactInfo.objects.get(phone_number=phone_number).user
                user.username = self.cleaned_data["email"]
                user.email = self.cleaned_data["email"]
                user.set_password(self.cleaned_data["password1"])
            user.save()

            # Create or update the UserContactInfo instance
            UserContactInfo.objects.update_or_create(
                user=user,
                defaults={'phone_number': self.cleaned_data.get('phone_number')}
            )
        return user
