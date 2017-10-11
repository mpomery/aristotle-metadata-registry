from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib.auth.models import User

from organizations.forms import SignUpForm


class RegistrySignUpForm(SignUpForm):
    """
    Form class for signing up a new user and new account.
    
    We explicitly force errors if they enter an existing user,
    or an existing registry slug
    """
    first_name = forms.CharField(max_length=50,
            help_text=_("The name of the organization"))
    last_name = forms.SlugField(max_length=50,
            help_text=_("The name in all lowercase, suitable for URL identification"))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )
        return email
TypeError: 'module' object is not iterable