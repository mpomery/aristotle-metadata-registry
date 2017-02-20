from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.identifier.models import ScopedIdentifier, Namespace


# TODO: Fix this method, it is a hot mess!... But it works.
# But it will require Django 1.9 - https://docs.djangoproject.com/en/1.9/topics/forms/formsets/#passing-custom-parameters-to-formset-forms
# Or some funky functional stuff - http://stackoverflow.com/a/624013/764357
def identifier_inlineformset_factory(model):

    class IdentifierForm(forms.ModelForm):
        class Meta:
            model = ScopedIdentifier
            fields = ('concept', 'namespace', 'identifier', 'version')

    base_formset = inlineformset_factory(
        MDR._concept, ScopedIdentifier,
        can_delete=True,
        fields=('concept', 'namespace', 'identifier', 'version'),
        extra=1,
        form=SlotForm
        )

    class SlotFormset(base_formset):
        def clean(self):
            slot_types_seen = set()
            for form in self.forms:
                if 'type' in form.cleaned_data.keys():
                    item = form.cleaned_data['concept'].item
                    slot_type = form.cleaned_data['type']

                    # Keep track of slot_types for cardinality
                    slot_type_in_form = slot_type in slot_types_seen
                    slot_types_seen.add(slot_type)

                    model = item.__class__
                    if not (slot_type.app_label == model._meta.app_label and slot_type.concept_type == model._meta.model_name):
                        raise forms.ValidationError(_("The selected slot type '%(slot_name)s' is not allowed on this concept type") % {'slot_name': slot_type.slot_name})

                    if slot_type.cardinality == SlotDefinition.CARDINALITY.singleton and slot_type_in_form:
                        raise forms.ValidationError(_("The selected slot type '%(slot_name)s' is only allowed to be included once") % {'slot_name': slot_type.slot_name})
    return SlotFormset