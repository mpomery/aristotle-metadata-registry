from django import forms
from django.forms.models import BaseModelFormSet
from aristotle_mdr.models import _concept, ValueDomain, ValueMeaning
from aristotle_mdr.contrib.autocomplete import widgets
from django.forms.models import modelformset_factory
from django.forms import ModelChoiceField, CharField

class HiddenOrderModelFormSet(BaseModelFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["ORDER"].widget = forms.HiddenInput()

def one_to_many_formset_excludes(item):

    extra_excludes = []
    if isinstance(item, ValueDomain):
        # Value Domain specific excludes
        if not item.conceptual_domain:
            extra_excludes.append('value_meaning')
        else:
            extra_excludes.append('meaning')

    return extra_excludes

def one_to_many_formset_filters(formset, item):

    if isinstance(item, ValueDomain) and item.conceptual_domain:
        vmqueryset = ValueMeaning.objects.filter(conceptual_domain=item.conceptual_domain)

        for form in formset:
            form.fields['value_meaning'].queryset = vmqueryset

    return formset

def one_to_many_formset_factory(model_to_add, model_to_add_field, ordering_field, extra_excludes=[]):
    _widgets = {}
    exclude_fields = [model_to_add_field, ordering_field]
    exclude_fields += extra_excludes

    for f in model_to_add._meta.fields:
        foreign_model = model_to_add._meta.get_field(f.name).related_model
        if foreign_model and issubclass(foreign_model, _concept):
            _widgets.update({
                f.name: widgets.ConceptAutocompleteSelect(
                    model=foreign_model
                )
            })
    for f in model_to_add._meta.many_to_many:
        foreign_model = model_to_add._meta.get_field(f.name).related_model
        if foreign_model and issubclass(foreign_model, _concept):
            _widgets.update({
                f.name: widgets.ConceptAutocompleteSelectMultiple(
                    model=foreign_model
                )
            })

    return modelformset_factory(
        model_to_add,
        formset=HiddenOrderModelFormSet,
        can_order=True,  # we assign this back to the ordering field
        can_delete=True,
        exclude=exclude_fields,
        # fields='__all__',
        extra=1,
        widgets=_widgets
        )


def one_to_many_formset_save(formset, item, model_to_add_field, ordering_field):

    item.save()  # do this to ensure we are saving reversion records for the value domain, not just the values
    formset.save(commit=False)
    for form in formset.forms:
        all_blank = not any(form[f].value() for f in form.fields if f is not ordering_field)
        if all_blank:
            continue
        if form['id'].value() not in [deleted_record['id'].value() for deleted_record in formset.deleted_forms]:
            # Don't immediately save, we need to attach the parent object
            value = form.save(commit=False)
            setattr(value, model_to_add_field, item)
            if ordering_field:
                setattr(value, ordering_field, form.cleaned_data['ORDER'])
            value.save()
    for obj in formset.deleted_objects:
        obj.delete()
    formset.save_m2m()
