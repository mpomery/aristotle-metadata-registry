from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareModelForm, UserAwareForm
from aristotle_mdr.forms import ChangeStatusForm
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from django.contrib.auth import get_user_model

from aristotle_mdr.contrib.autocomplete import widgets
from .utils import RegistrationAuthorityMixin


class RequestReviewForm(RegistrationAuthorityMixin, UserAwareModelForm):
    registration_date = forms.DateField(
        required=False,
        label=_("Registration date"),
        widget=BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
        initial=timezone.now()
    )
    state = forms.ChoiceField(choices=MDR.STATES, widget=forms.RadioSelect)
    cascadeRegistration = forms.ChoiceField(
        initial=False,
        required=False,
        choices=[(0, _('No')), (1, _('Yes'))],
        label=_("Do you want to update the registration of associated items?")
    )

    def __init__(self, *args, **kwargs):
        # self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.set_registration_authority_field(
            field_name="registration_authority"
        )

    class Meta:
        model = MDR.ReviewRequest
        fields = [
            'state', 'registration_authority', 'message',
            'registration_date', 'cascade_registration'
        ]


class RequestReviewCancelForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        fields = []


class RequestReviewRejectForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        fields = ['response']


class RequestReviewAcceptForm(UserAwareForm):
    response = forms.CharField(
        max_length=512,
        required=False,
        label=_("Reply to the original review request below."),
        widget=forms.Textarea
    )


class AddRegistrationUserForm(UserAwareForm):
    roles = forms.MultipleChoiceField(
        label=_("Registry roles"),
        choices=sorted(MDR.RegistrationAuthority.roles.items()),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    user = forms.ModelChoiceField(
        label=_("Select user"),
        queryset=get_user_model().objects.filter(is_active=True),
        widget=widgets.UserAutocompleteSelect(),
        initial=None,
    )


class ChangeRegistrationUserRolesForm(UserAwareForm):
    roles = forms.MultipleChoiceField(
        label=_("Registry roles"),
        choices=sorted(MDR.RegistrationAuthority.roles.items()),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
