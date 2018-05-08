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

def one_to_many_formset_factory(model_to_add, model_to_add_field, ordering_field, extra_excludes=[]):
    # creates a one to many formset
    # model_to_add is weak entity class, model_to_add_field is the foriegn key field name

    exclude_fields = [model_to_add_field, ordering_field]
    exclude_fields += extra_excludes

    _widgets = get_aristotle_widgets(model_to_add)

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

def through_formset_factory(model, excludes=[]):

    _widgets = get_aristotle_widgets(model)

    return modelformset_factory(
        model,
        formset=HiddenOrderModelFormSet,
        can_order=True,  # we assign this back to the ordering field
        can_delete=True,
        exclude=excludes,
        extra=1,
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
    for field in field_model._meta.get_fields():
        if (field.is_relation):
            if (field.related_model == search_model):
                model_to_add_field = field.name
                break

    return model_to_add_field


def get_weak_formset(entity, item, search_model):
    # where entity is an entry in serialize_weak_entities

    field_model = getattr(item, entity[1]).model
    model_to_add_field = self.get_weak_model_field(field_model, search_model)

    extra_excludes = one_to_many_formset_excludes(item, field_model)
    formset = one_to_many_formset_factory(field_model, model_to_add_field, field_model.ordering_field, extra_excludes)
    formset_info = {
        'formset': formset,
        'model_field': model_to_add_field,
        'prefix': entity[0],
        'ordering': field_model.ordering_field,
    }

    return formset_info

def get_order_formset(item, through, postdata=None):
    excludes = ['order'] + through['item_fields']
    formset = through_formset_factory(through['model'], excludes)

    fsargs = {'prefix': through['field_name']}

    if len(through['item_fields']) == 1:
        through_filter = {through['item_fields'][0]: item}
        fsargs.update({'queryset': through['model'].objects.filter(**through_filter)})

    if postdata:
        fsargs.update({'data': postdata})

    formset_instance = formset(**fsargs)

    return formset_instance
