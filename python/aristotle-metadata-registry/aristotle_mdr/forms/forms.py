from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.forms.models import ModelMultipleChoiceField

from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from aristotle_mdr.widgets.widgets import TableCheckboxSelect
import aristotle_mdr.models as MDR
from aristotle_mdr.perms import user_can_edit
from aristotle_mdr.forms.creation_wizards import UserAwareForm
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.utils import status_filter
from aristotle_mdr import perms

from django.forms.models import modelformset_factory

from .utils import RegistrationAuthorityMixin


class UserSelfEditForm(forms.Form):
    template = "aristotle_mdr/userEdit.html"

    first_name = forms.CharField(required=False, label=_('First Name'))
    last_name = forms.CharField(required=False, label=_('Last Name'))
    email = forms.EmailField(required=False, label=_('Email Address'))


# For stating that an item deprecates other items.
class DeprecateForm(forms.Form):
    olderItems = forms.ModelMultipleChoiceField(
        queryset=MDR._concept.objects.all(),
        label="Supersede older items",
        required=False,
        widget=widgets.ConceptAutocompleteSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item')
        self.qs = kwargs.pop('qs')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['olderItems'] = forms.ModelMultipleChoiceField(
            queryset=self.qs,
            label=_("Supersede older items"),
            required=False,
            initial=self.item.supersedes.all(),
            widget=widgets.ConceptAutocompleteSelectMultiple(
                model=self.item._meta.model
            )
        )

    def clean_olderItems(self):
        olderItems = self.cleaned_data['olderItems']
        if self.item in olderItems:
            raise forms.ValidationError("An item may not supersede itself")
        for i in olderItems:
            if not user_can_edit(self.user, i):
                raise forms.ValidationError("You cannot supersede an item that you do not have permission to edit")
        return olderItems


# For superseding an item with a newer one.
class SupersedeForm(forms.Form):
    newerItem = forms.ModelChoiceField(
        queryset=MDR._concept.objects.all(),
        empty_label="None",
        label=_("Superseded by"),
        required=False,
        widget=widgets.ConceptAutocompleteSelect()
    )

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item')
        self.qs = kwargs.pop('qs')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['newerItem']=forms.ModelChoiceField(
            queryset=self.qs,
            empty_label="None",
            label=_("Superseded by"),
            initial=self.item.superseded_by,
            required=False,
            widget=widgets.ConceptAutocompleteSelect(
                model=self.item._meta.model
            )
        )

    def clean_newerItem(self):
        item = self.cleaned_data['newerItem']
        if not item:
            return None
        if self.item.id == item.id:
            raise forms.ValidationError("An item may not supersede itself")
        if not user_can_edit(self.user, item):
            raise forms.ValidationError("You cannot supersede with an item that you do not have permission to edit")
        return item


class ChangeStatusForm(RegistrationAuthorityMixin, UserAwareForm):
    state = forms.ChoiceField(choices=MDR.STATES, widget=forms.RadioSelect)
    registrationDate = forms.DateField(
        required=False,
        label=_("Registration date"),
        widget=BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
        initial=timezone.now()
    )
    cascadeRegistration = forms.ChoiceField(
        initial=0,
        choices=[(0, _('No')), (1, _('Yes'))],
        label=_("Do you want to request a status change for associated items?")
    )
    changeDetails = forms.CharField(
        max_length=512,
        required=False,
        label=_("Why is the status being changed for these items?"),
        widget=forms.Textarea
    )
    registrationAuthorities = forms.ChoiceField(
        label="Registration Authorities",
        choices=MDR.RegistrationAuthority.objects.none(),
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_registration_authority_field(
            field_name="registrationAuthorities", qs=self.user.profile.registrarAuthorities
        )

    def clean_cascadeRegistration(self):
        return self.cleaned_data['cascadeRegistration'] == "1"

    def clean_registrationAuthorities(self):
        value = self.cleaned_data['registrationAuthorities']
        return [
            MDR.RegistrationAuthority.objects.get(id=int(value))
        ]

    def clean_state(self):
        state = self.cleaned_data['state']
        state = int(state)
        MDR.STATES[state]
        return state


class ReviewChangesForm(forms.Form):

    def __init__(self, queryset, static_content, ra, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_list'] = ReviewChangesChoiceField(
            queryset=queryset,
            static_content=static_content,
            ra=ra,
            user=user,
            label=_("Select the items you would like to update")
        )


# Thanks http://stackoverflow.com/questions/6958708/grappelli-to-hide-sortable-field-in-inline-sortable-django-admin
class PermissibleValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = MDR.PermissibleValue
        fields = "__all__"


class CompareConceptsForm(forms.Form):
    item_a = forms.ModelChoiceField(
        queryset=MDR._concept.objects.none(),
        empty_label="None",
        label=_("First item"),
        required=True,
        widget=widgets.ConceptAutocompleteSelect()
    )
    item_b = forms.ModelChoiceField(
        queryset=MDR._concept.objects.none(),
        empty_label="None",
        label=_("Second item"),
        required=True,
        widget=widgets.ConceptAutocompleteSelect()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.qs = kwargs.pop('qs').visible(self.user)
        super().__init__(*args, **kwargs)

        self.fields['item_a'] = forms.ModelChoiceField(
            queryset=self.qs,
            empty_label="None",
            label=_("First item"),
            required=True,
            widget=widgets.ConceptAutocompleteSelect()
        )
        self.fields['item_b']=forms.ModelChoiceField(
            queryset=self.qs,
            empty_label="None",
            label=_("Second item"),
            required=True,
            widget=widgets.ConceptAutocompleteSelect()
        )


# ------------ Form Fields ------------


class ReviewChangesChoiceField(ModelMultipleChoiceField):

    def __init__(self, queryset, static_content, ra, user, **kwargs):

        extra_info = self.build_extra_info(queryset, ra, user)

        headers = {
            'select': '',
            'name': '',
            'old_reg_date': 'Old Registration Date',
            'type': '',
            'old': 'Old State',
            'new_state': 'New State',
            'new_reg_date': 'New Registration Date',
        }

        top_header = [
            {'text': 'Select'},
            {'text': 'Name'},
            {'text': 'Type'},
            {'text': 'Previous','colspan': 2},
            {'text': 'New','colspan': 2}
        ]
        
        order = ['select', 'name', 'type', 'old', 'old_reg_date', 'new_state', 'new_reg_date']

        self.widget = TableCheckboxSelect(
            extra_info=extra_info,
            static_info=static_content,
            attrs={'tableclass': 'table'},
            headers=headers,
            top_header=top_header,
            order=order
        )

        super().__init__(queryset, **kwargs)

    def build_extra_info(self, queryset, ra, user):

        extra_info = {}
        subclassed_queryset = queryset.select_subclasses()
        statuses = MDR.Status.objects.filter(concept__in=queryset, registrationAuthority=ra).select_related('concept')
        statuses = status_filter(statuses).order_by("-registrationDate", "-created")

        # Build a dict mapping concepts to their status data
        # So that no additional status queries need to be made
        states_dict = {}
        for status in statuses:
            state_name = str(MDR.STATES[status.state])
            reg_date = status.registrationDate
            if status.concept.id not in states_dict:
                states_dict[status.concept.id] = {'name': state_name, 'reg_date': reg_date}

        for concept in subclassed_queryset:
            innerdict = {}
            # Get class name
            innerdict.update({'type': concept.__class__.get_verbose_name()})

            try:
                state_info = states_dict[concept.id]
            except KeyError:
                state_info = None

            if state_info:
                innerdict.update({'old': state_info['name'], 'old_reg_date': state_info['reg_date']})

            innerdict.update({'perm': perms.user_can_change_status(user, concept)})

            extra_info.update({concept.id: innerdict})

        return extra_info
