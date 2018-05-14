from django import forms
from django.core.exceptions import PermissionDenied, FieldDoesNotExist
from django.urls import reverse
from django.db import transaction
from django.forms.models import modelformset_factory
from django.forms import formset_factory
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, TemplateView, View

from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.models import _concept, ValueDomain, AbstractValue
from aristotle_mdr.perms import user_can_edit, user_can_view
from aristotle_mdr.utils import construct_change_message
from aristotle_mdr.contrib.generic.forms import (
    ordered_formset_factory, ordered_formset_save,
    one_to_many_formset_excludes, one_to_many_formset_filters,
    HiddenOrderFormset, HiddenOrderModelFormSet
)
import reversion
import inspect
import re

import logging
logger = logging.getLogger(__name__)


def generic_foreign_key_factory_view(request, **kwargs):
    item = get_object_or_404(_concept, pk=kwargs['iid']).item
    field = None

    for f in item._meta.fields:
        if f.name.lower() == kwargs['fk_field'].lower():
            field = f.name

    if not field:
        raise Http404

    return GenericAlterForeignKey.as_view(
        model_base=item.__class__,
        model_base_field=field,
        form_title=_('Add Object Class')
    )(request, **kwargs)


class GenericWithItemURLView(View):
    user_checks = []
    permission_checks = [user_can_view]
    model_base = _concept
    item_kwarg = "iid"

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(self.model_base, pk=self.kwargs[self.item_kwarg])

        if not (
            self.item and
            all([perm(request.user, self.item) for perm in self.permission_checks]) and
            all([perm(request.user) for perm in self.user_checks])
        ):
            if request.user.is_anonymous():
                return redirect(reverse('friendly_login') + '?next=%s' % request.path)
            else:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['item'] = self.item
        context['submit_url'] = self.request.get_full_path()
        return context

    def get_success_url(self):
        return self.item.get_absolute_url()


class GenericWithItemURLFormView(GenericWithItemURLView, FormView):
    pass


class GenericAlterManyToSomethingFormView(GenericWithItemURLFormView):
    permission_checks = [user_can_edit]
    model_base = None
    model_to_add = None
    model_base_field = None
    form_title = None
    form_submit_text = _('Save')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_to_add'] = self.model_to_add
        context['model_base'] = self.model_base
        context['item'] = self.item
        context['form_title'] = self.form_title or _('Add child item')
        context['form_submit_text'] = self.form_submit_text
        return context


class GenericAlterForeignKey(GenericAlterManyToSomethingFormView):
    """
    A view that provides a framework for altering ManyToOne relationships
    (Include through models from ManyToMany relationships)
    from one 'base' object to many others.

    The URL pattern must pass a kwarg with the name `iid` that is the object from the
    `model_base` to use as the main link for the many to many relation.

    * `model_base` - mandatory - The model with the instance to be altered
    * `model_to_add` - mandatory - The model that has instances we will link to the base.
    * `template_name`
        - optional - The template used to display the form.
        - default - "aristotle_mdr/generic/actions/alter_foreign_key.html"
    * `model_base_field` - mandatory - the name of the field that goes from the `model_base` to the `model_to_add`.
    * `model_to_add_field` - mandatory - the name of the field on the `model_to_add` model that links to the `model_base` model.
    * `form_title` - Title for the form

    For example: If we have a many to many relationship from `DataElement`s to
    `Dataset`s, to alter the `DataElement`s attached to a `Dataset`, `Dataset` is the
    `base_model` and `model_to_add` is `DataElement`.
    """

    template_name = "aristotle_mdr/generic/actions/alter_foreign_key.html"
    model_to_add_field = None
    form = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_add_another_text'] = self.form_submit_text or _('Add another')
        form = self.form or self.get_form()(instance=self.item)
        context['form'] = form
        return context

    def get_form(self, form_class=None):
        foreign_model = self.model_base._meta.get_field(self.model_base_field).related_model
        qs = foreign_model.objects.visible(self.request.user)
        model_base_field = self.model_base_field

        class FKOnlyForm(forms.ModelForm):
            class Meta():
                model = self.model_base
                fields = (self.model_base_field,)
                widgets = {
                    self.model_base_field: widgets.ConceptAutocompleteSelect(
                        model=foreign_model
                    )
                }

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields[model_base_field].queryset = qs

        return FKOnlyForm

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        self.form = form(self.request.POST, self.request.FILES, instance=self.item)
        if self.form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                self.form.save()  # do this to ensure we are saving reversion records for the value domain, not just the values
                reversion.revisions.set_user(request.user)
                reversion.revisions.set_comment(
                    _("Altered relationship of '%s' on %s") % (self.model_base_field, self.item)
                )

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class GenericAlterManyToManyView(GenericAlterManyToSomethingFormView):
    """
    A view that provides a framework for altering ManyToMany relationships from
    one 'base' object to many others.

    The URL pattern must pass a kwarg with the name `iid` that is the object from the
    `model_base` to use as the main link for the many to many relation.

    * `model_base` - mandatory - The model with the instance to be altered
    * `model_to_add` - mandatory - The model that has instances we will link to the base.
    * `template_name`
        - optional - The template used to display the form.
        - default - "aristotle_mdr/generic/actions/alter_many_to_many.html"
    * `model_base_field` - mandatory - the field name that goes from the `model_base` to the `model_to_add`.
    * `form_title` - Title for the form

    For example: If we have a many to many relationship from `DataElement`s to
    `Dataset`s, to alter the `DataElement`s attached to a `Dataset`, `Dataset` is the
    `base_model` and `model_to_add` is `DataElement`.
    """

    template_name = "aristotle_mdr/generic/actions/alter_many_to_many.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context

    def get_form_class(self):
        class M2MForm(forms.Form):
            items_to_add = forms.ModelMultipleChoiceField(
                queryset=self.model_to_add.objects.visible(self.request.user),
                label="Attach",
                required=False,
                widget=widgets.ConceptAutocompleteSelectMultiple(
                    model=self.model_to_add
                )
            )
        return M2MForm

    def get_initial(self):
        return {
            'items_to_add': getattr(self.item, self.model_base_field).all()
        }

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.item.__setattr__(self.model_base_field, form.cleaned_data['items_to_add'])
        self.item.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericAlterManyToManyOrderView(GenericAlterManyToManyView):

    template_name = "aristotle_mdr/generic/actions/alter_many_to_many_order.html"

    def get_form_class(self):
        class M2MOrderForm(forms.Form):
            item_to_add = forms.ModelChoiceField(
                queryset=self.model_to_add.objects.visible(self.request.user),
                label="Attach",
                required=False,
                widget=widgets.ConceptAutocompleteSelect(
                    model=self.model_to_add
                )
            )
        return M2MOrderForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        num_items = getattr(self.item, self.model_base_field).count()

        context['form_add_another_text'] = _('Add Another')

        if 'formset' in kwargs:
            context['formset'] = kwargs['formset']
        else:
            formset_initial = self.get_formset_initial()
            formset = self.get_formset()(initial=formset_initial)
            context['formset'] = formset

        if 'message' in kwargs:
            context['error_message'] = kwargs['message']

        return context

    def get_form(self):
        return None

    def dispatch(self, request, *args, **kwargs):

        self.through_model = self.model_base._meta.get_field(self.model_base_field).remote_field.through

        self.base_through_field = None
        self.related_through_field = None
        for field in self.through_model._meta.get_fields():
            if field.is_relation:
                if field.related_model == self.model_base:
                    self.base_through_field = field.name
                elif field.related_model == self.model_to_add:
                    self.related_through_field = field.name

        # Check if either is None
        if self.base_through_field is None or self.related_through_field is None:
            return self.error_with_message('Many to Many edit could not be performed on this object')

        return super().dispatch(request, *args, **kwargs)

    def get_formset(self):

        formclass = self.get_form_class()
        return formset_factory(formclass, formset=HiddenOrderFormset, can_order=True, can_delete=True, extra=0)

    def get_formset_initial(self):
        # Build initial
        filter_args = {self.base_through_field: self.item}
        through_items = self.through_model.objects.filter(**filter_args).order_by('order')

        initial = []
        for item in through_items:
            initial.append({
                'item_to_add': getattr(item, self.related_through_field),
                'ORDER': item.order
            })

        return initial

    def error_with_message(self, message):
        return self.render_to_response(self.get_context_data(message=message))

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):

        formset = self.get_formset()
        filled_formset = formset(self.request.POST)

        if filled_formset.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():

                model_arglist = []
                model_arglist_update = []
                model_arglist_delete = []
                change_message = []

                for form in filled_formset.ordered_forms:
                    to_add = form.cleaned_data['item_to_add']

                    if to_add:
                        model_args = {
                            self.base_through_field: self.item,
                            self.related_through_field: to_add,
                            'order': form.cleaned_data['ORDER']
                        }

                        model_arglist.append(model_args)
                        change_message.append('Added {} to {} {}'.format(to_add.name, self.item.name, self.model_base_field))

                # Delete existing links

                through_args = {
                    self.base_through_field: self.item
                }
                self.through_model.objects.filter(**through_args).delete()

                # Create new links
                for model_args in model_arglist:
                    self.through_model.objects.create(**model_args)

                reversion.revisions.set_user(request.user)
                reversion.revisions.set_comment(change_message)

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.formset_invalid(filled_formset)


class GenericAlterOneToManyView(GenericAlterManyToSomethingFormView):
    """
    A view that provides a framework for altering ManyToOne relationships
    (Include through models from ManyToMany relationships)
    from one 'base' object to many others.

    The URL pattern must pass a kwarg with the name `iid` that is the object from the
    `model_base` to use as the main link for the many to many relation.

    * `model_base` - mandatory - The model with the instance to be altered
    * `model_to_add` - mandatory - The model that has instances we will link to the base.
    * `template_name`
        - optional - The template used to display the form.
        - default - "aristotle_mdr/generic/actions/alter_many_to_many.html"
    * `model_base_field` - mandatory - the name of the field that goes from the `model_base` to the `model_to_add`.
    * `model_to_add_field` - mandatory - the name of the field on the `model_to_add` model that links to the `model_base` model.
    * `ordering_field` - optional - name of the ordering field, if entered this field is hidden and updated using a drag-and-drop library
    * `form_add_another_text` - optional - string used for the button to add a new row to the form - defaults to "Add another"
    * `form_title` - Title for the form

    For example: If we have a many to many relationship from `DataElement`s to
    `Dataset`s, to alter the `DataElement`s attached to a `Dataset`, `Dataset` is the
    `base_model` and `model_to_add` is `DataElement`.
    """

    template_name = "aristotle_mdr/generic/actions/alter_one_to_many.html"
    model_to_add_field = None
    ordering_field = None
    form_add_another_text = None

    formset = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_add_another_text'] = self.form_add_another_text or _('Add another')
        num_items = getattr(self.item, self.model_base_field).count()
        formset = self.formset or self.get_formset()(
            queryset=getattr(self.item, self.model_base_field).all(),
            )
        context['formset'] = one_to_many_formset_filters(formset, self.item)
        return context

    def get_form(self, form_class=None):
        return None

    def get_formset(self):

        extra_excludes = one_to_many_formset_excludes(self.item, self.model_to_add)
        all_excludes = [self.model_to_add_field, self.ordering_field] + extra_excludes
        formset = ordered_formset_factory(self.model_to_add, all_excludes)

        return formset

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        GenericFormSet = self.get_formset()
        self.formset = GenericFormSet(self.request.POST, self.request.FILES)
        formset = self.formset
        if formset.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                ordered_formset_save(formset, self.item, self.model_to_add_field, self.ordering_field)

                # formset.save(commit=True)
                reversion.revisions.set_user(request.user)
                reversion.revisions.set_comment(construct_change_message(request, None, [formset]))

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class ExtraFormsetMixin:

    # Mixin of utils function for adding addtional formsets to a view
    # extra_formsets must contain formset, type, title and saveargs
    # See EditItemView for example usage

    def save_formsets(self, extra_formsets):
        for formsetinfo in extra_formsets:
            if formsetinfo['saveargs']:
                ordered_formset_save(**formsetinfo['saveargs'])
            else:
                formsetinfo['formset'].save()

    def validate_formsets(self, extra_formsets):
        invalid = False

        for formsetinfo in extra_formsets:
            if not formsetinfo['formset'].is_valid():
                invalid = True

        return invalid

    def get_formset_context(self, extra_formsets):
        context = {}

        for formsetinfo in extra_formsets:
            type = formsetinfo['type']
            if type == 'identifiers':
                context['identifier_FormSet'] = formsetinfo['formset']
            elif type == 'slot':
                context['slots_FormSet'] = formsetinfo['formset']
            elif type == 'weak':
                if 'weak_formsets' not in context.keys():
                    context['weak_formsets'] = []
                context['weak_formsets'].append({'formset': formsetinfo['formset'], 'title': formsetinfo['title']})
            elif type == 'through':
                if 'through_formsets' not in context.keys():
                    context['through_formsets'] = []
                context['through_formsets'].append({'formset': formsetinfo['formset'], 'title': formsetinfo['title']})

        return context

    def get_extra_formsets(self, item=None, postdata=None):
        # Item can be a class or an object
        # This is so we can reuse this function in creation wizards

        extra_formsets = []

        if inspect.isclass(item):
            is_class = True
            add_item = None
        else:
            is_class = False
            add_item = item

        through_list = self.get_m2m_through(item)
        for through in through_list:

            if not is_class:
                formset = self.get_order_formset(through, item, postdata)
            else:
                formset = self.get_order_formset(through, postdata=postdata)

            extra_formsets.append({
                'formset': formset,
                'type': 'through',
                'title': through['field_name'].title(),
                'saveargs': {
                    'formset': formset,
                    'item': add_item,
                    'model_to_add_field': through['item_field'],
                    'ordering_field': 'order'
                }
            })

        weak_list = self.get_m2m_weak(item)
        for weak in weak_list:

            if not is_class:
                formset = self.get_weak_formset(weak, item, postdata)
            else:
                formset = self.get_weak_formset(weak, postdata=postdata)

            title = weak['model'].__name__
            # add spaces before capital letters
            title = re.sub(r"\B([A-Z])", r" \1", title)

            if hasattr(weak['model'], 'ordering_field'):
                order_field = weak['model'].ordering_field
            else:
                order_field = 'order'

            extra_formsets.append({
                'formset': formset,
                'type': 'weak',
                'title': title,
                'saveargs': {
                    'formset': formset,
                    'item': add_item,
                    'model_to_add_field': weak['item_field'],
                    'ordering_field': order_field
                }
            })

        return extra_formsets

    def get_order_formset(self, through, item=None, postdata=None):
        excludes = ['order', through['item_field']]
        formset = ordered_formset_factory(through['model'], excludes)

        fsargs = {'prefix': through['field_name']}

        if through['item_field']:
            if item:
                through_filter = {through['item_field']: item}
                fsargs['queryset'] = through['model'].objects.filter(**through_filter)
            else:
                fsargs['queryset'] = through['model'].objects.none()

        if postdata:
            fsargs['data'] = postdata

        formset_instance = formset(**fsargs)

        return formset_instance

    def get_weak_formset(self, weak, item=None, postdata=None):

        model_to_add_field = weak['item_field']

        if 'prefix' in weak:
            fsargs = {'prefix': weak['prefix']}
        else:
            fsargs = {'prefix': weak['field_name']}

        if item:
            extra_excludes = one_to_many_formset_excludes(item, weak['model'])
            fsargs['queryset'] = getattr(item, weak['field_name']).all()
        else:
            if issubclass(weak['model'], AbstractValue):
                extra_excludes = ['value_meaning']
            else:
                extra_excludes = []
            fsargs['queryset'] = weak['model'].objects.none()

        if postdata:
            fsargs['data'] = postdata

        all_excludes = [model_to_add_field, weak['model'].ordering_field] + extra_excludes
        formset = ordered_formset_factory(weak['model'], all_excludes)

        final_formset = formset(**fsargs)

        return final_formset

    def get_model_field(self, model, search_model):
        # get the field in the model that we are adding so it can be excluded from form
        model_to_add_field = ''
        for field in model._meta.get_fields():
            if (field.is_relation):
                if (field.related_model == search_model):
                    model_to_add_field = field.name
                    break

        return model_to_add_field

    def get_m2m_through(self, item):
        through_list = []

        if inspect.isclass(item):
            check_class = item
        else:
            check_class = item.__class__

        excludes = getattr(check_class, 'through_edit_excludes', [])
        if not excludes:
            excludes = []

        for field in check_class._meta.get_fields():
            if field.many_to_many:
                if hasattr(field.remote_field, 'through'):
                    through = field.remote_field.through
                    if not through._meta.auto_created:
                        item_field = self.get_model_field(through, check_class)
                        if item_field and field.name not in excludes:
                            through_list.append({'field_name': field.name, 'model': through, 'item_field': item_field})

        return through_list

    def get_m2m_weak(self, item):
        weak_list = []

        if inspect.isclass(item):
            check_class = item
        else:
            check_class = item.__class__

        excludes = getattr(check_class, 'edit_page_excludes', [])
        if not excludes:
            excludes = []

        if hasattr(check_class, 'serialize_weak_entities'):

            weak = check_class.serialize_weak_entities

            for entity in weak:

                if entity[0] not in excludes:

                    try:
                        field = check_class._meta.get_field(entity[1])
                    except FieldDoesNotExist:
                        if entity[1].endswith('_set'):
                            # entity[1] contains the related name for an object
                            # This can be different to the relation name on the model
                            # If related_name was not set on the foreign key
                            # this code deals with the case where it was auto generated by django
                            try:
                                field = check_class._meta.get_field(entity[1][:-4])
                            except FieldDoesNotExist:
                                continue
                        else:
                            continue

                    item_field = self.get_model_field(field.related_model, check_class)
                    if item_field:
                        weak_list.append({'prefix': entity[0], 'field_name': entity[1], 'model': field.related_model, 'item_field': item_field})

        return weak_list


class ConfirmDeleteView(GenericWithItemURLView, TemplateView):
    confirm_template = "aristotle_mdr/generic/actions/confirm_delete.html"
    template_name = "aristotle_mdr/generic/actions/confirm_delete.html"
    form_delete_button_text = _("Delete")
    warning_text = _("You are about to delete something, confirm below, or click cancel to return to the item.")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_title'] = self.form_title or _('Add child item')
        context['form_delete_button_text'] = self.form_delete_button_text
        context['warning_text'] = self.get_warning_text()
        return context

    def get_warning_text(self):
        return self.warning_text

    def perform_deletion(self):
        raise NotImplementedError("This must be overridden in a subclass")

    def post(self, *args, **kwargs):
        self.perform_deletion()
        return HttpResponseRedirect(self.get_success_url())
