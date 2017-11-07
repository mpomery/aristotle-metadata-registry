from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from organizations.forms import SignUpForm

from aristotle_mdr.forms.utils import FormRequestMixin
from aristotle_mdr.utils import fetch_aristotle_settings


class UserInvitationForm(FormRequestMixin, forms.Form):
    email_list = forms.CharField(
        widget=forms.Textarea,
        label="User emails",
        help_text="Enter one email per line."
    )

    def clean_email_list(self):
        data = self.cleaned_data['email_list']
        emails = [e.strip() for e in data.split('\n')]

        email_suffixes = fetch_aristotle_settings().get('USER_EMAIL_RESTRICTIONS', [])

        errors = []
        for i, email in enumerate(emails):
            if email.strip() == "":
                continue
            try:
                validate_email(email)
            except ValidationError:
                errors.append(
                    _("The email '%(email)s' on line %(line_no)d is not valid") % {"email": email, "line_no": i+1}
                )

        if errors:
            raise ValidationError(errors)

        emails = [e.strip() for e in data.split('\n') if e != ""]
        self.cleaned_data['email_list'] = "\n".join(emails)

        self.emails = emails
