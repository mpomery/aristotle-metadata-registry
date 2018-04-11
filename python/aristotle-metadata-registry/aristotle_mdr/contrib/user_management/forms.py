from django import forms
from django.utils.translation import ugettext_lazy as _

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from aristotle_mdr.forms.utils import FormRequestMixin
from aristotle_mdr.utils import fetch_aristotle_settings

from organizations.backends.forms import UserRegistrationForm


class UserInvitationForm(FormRequestMixin, forms.Form):
    email_list = forms.CharField(
        widget=forms.Textarea,
        label="User emails",
        help_text="Enter one email per line."
    )

    def clean_email_list(self):
        data = self.cleaned_data['email_list']
        emails = [e.strip() for e in data.split('\n')]

        errors = []
        for i, email in enumerate(emails):
            if email.strip() == "":
                continue
            try:
                validate_email(email)
            except ValidationError:
                errors.append(
                    _("The email '%(email)s' on line %(line_no)d is not valid") % {"email": email, "line_no": i + 1}
                )

        if errors:
            raise ValidationError(errors)

        emails = [e.strip() for e in data.split('\n') if e != ""]
        self.cleaned_data['email_list'] = "\n".join(emails)

        self.emails = emails

class AristotleUserRegistrationForm(UserRegistrationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields.pop('first_name')
        self.fields.pop('last_name')
        self.initial.pop('username')
