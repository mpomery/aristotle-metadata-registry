from django import forms
from django.forms.models import BaseModelFormSet
from aristotle_mdr.models import _concept, ValueDomain, ValueMeaning
from aristotle_mdr.contrib.autocomplete import widgets
from django.forms.models import modelformset_factory
from django.forms import ModelChoiceField, CharField
from django.forms.formsets import BaseFormSet
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from django.db.models import DateField
from aristotle_mdr.models import AbstractValue


import logging
logger = logging.getLogger(__name__)

datePickerOptions = {
    "format": "YYYY-MM-DD",
    "useCurrent": False,
    "widgetPositioning": {
        "horizontal": "left",
        "vertical": "auto"
    }
}


class HiddenOrderFormset(BaseFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["ORDER"].widget = forms.HiddenInput()


class HiddenOrderModelFormSet(BaseModelFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["ORDER"].widget = forms.HiddenInput()


def one_to_many_formset_excludes(item, model_to_add):
    # creates a list of extra fields to be excluded based on the item related to the weak entity
    extra_excludes = []
    if isinstance(item, ValueDomain):
        # Value Domain specific excludes
        if issubclass(model_to_add, AbstractValue):
            if not item.conceptual_domain:
                extra_excludes.append('value_meaning')
            else:
                extra_excludes.append('meaning')

    return extra_excludes


def one_to_many_formset_filters(formset, item):
    # applies different querysets to the forms after they are instanciated
    if isinstance(item, ValueDomain) and item.conceptual_domain:
        # Only show value meanings from this items conceptual domain
        vmqueryset = ValueMeaning.objects.filter(conceptual_domain=item.conceptual_domain)

        for form in formset:
            if issubclass(form._meta.model, AbstractValue):
                form.fields['value_meaning'].queryset = vmqueryset

    return formset


def get_aristotle_widgets(model):

    _widgets = {}

    for f in model._meta.fields:
        foreign_model = model._meta.get_field(f.name).related_model
        if foreign_model and issubclass(foreign_model, _concept):
            _widgets.update({
                f.name: widgets.ConceptAutocompleteSelect(
                    model=foreign_model
                )
            })

        if isinstance(model._meta.get_field(f.name), DateField):
            _widgets.update({
                f.name: BootstrapDateTimePicker(options=datePickerOptions)
            })

    for f in model._meta.many_to_many:
        foreign_model = model._meta.get_field(f.name).related_model
        if foreign_model and issubclass(foreign_model, _concept):
            _widgets.update({
                f.name: widgets.ConceptAutocompleteSelectMultiple(
                    model=foreign_model
                )
            })

    return _widgets


def ordered_formset_factory(model, excludes=[]):

    _widgets = get_aristotle_widgets(model)

    return modelformset_factory(
        model,
        formset=HiddenOrderModelFormSet,
        can_order=True,  # we assign this back to the ordering field
        can_delete=True,
        exclude=excludes,
        extra=0,
        widgets=_widgets
    )

def ordered_formset_save(formset, item, model_to_add_field, ordering_field):

    item.save()  # do this to ensure we are saving reversion records for the value domain, not just the values
    formset.save(commit=False) # Save formset so we have access to deleted_objects and save_m2m

    for form in formset.ordered_forms:
        # Loop through the forms so we can add the order value to the ordering field
        # ordered_forms does not contain forms marked for deletion
        obj = form.save(commit=False)
        setattr(obj, model_to_add_field, item)
        setattr(obj, ordering_field, form.cleaned_data['ORDER'])
        obj.save()

    for obj in formset.deleted_objects:
        # Delete objects marked for deletion
        obj.delete()

    # Save any m2m relations on the ojects (not actually needed yet)
    formset.save_m2m()


def get_weak_model_field(model, search_model):
    # get the field in the model that we are adding so it can be excluded from form
    model_to_add_field = ''
    for field in model._meta.get_fields():
        if (field.is_relation):
            if (field.related_model == search_model):
                model_to_add_field = field.name
                break

    return model_to_add_field


def get_weak_formset(entity, model, item=None, field_model=None, postdata=None, queryset=None):
    # where entity is an entry in serialize_weak_entities

    if not field_model:
        field_model = getattr(item, entity[1]).model

    model_to_add_field = get_weak_model_field(field_model, model)

    if item:
        extra_excludes = one_to_many_formset_excludes(item, field_model)
    else:
        if issubclass(model, ValueDomain):
            extra_excludes = ['value_meaning']
        else:
            extra_excludes = []

    all_excludes = [model_to_add_field, field_model.ordering_field] + extra_excludes
    formset = ordered_formset_factory(field_model, all_excludes)

    final_formset = formset(prefix=entity[0], data=postdata, queryset=queryset)

    formset_info = {
        'formset': final_formset,
        'model_field': model_to_add_field,
        'ordering': field_model.ordering_field,
    }

    return formset_info

def get_order_formset(through, item=None, postdata=None):
    excludes = ['order'] + through['item_fields']
    formset = ordered_formset_factory(through['model'], excludes)

    fsargs = {'prefix': through['field_name']}

    if len(through['item_fields']) == 1:
        if item:
            through_filter = {through['item_fields'][0]: item}
            fsargs.update({'queryset': through['model'].objects.filter(**through_filter)})
        else:
            fsargs.update({'queryset': through['model'].objects.none()})

    if postdata:
        fsargs.update({'data': postdata})

    formset_instance = formset(**fsargs)

    return formset_instance
