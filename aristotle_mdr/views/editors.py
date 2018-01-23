from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView, DetailView, UpdateView
)

import reversion

from aristotle_mdr.utils import (
    concept_to_clone_dict,
    construct_change_message, url_slugify_concept, is_active_module
)
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR

from aristotle_mdr.views.utils import ObjectLevelPermissionRequiredMixin

import logging

from aristotle_mdr.contrib.generic.forms import one_to_many_formset_factory, one_to_many_formset_save

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class ConceptEditFormView(ObjectLevelPermissionRequiredMixin):
    raise_exception = True
    redirect_unauthenticated_users = True
    object_level_permissions = True
    model = MDR._concept
    pk_url_kwarg = 'iid'

    def dispatch(self, request, *args, **kwargs):
        self.item = super().get_object().item
        self.model = self.item.__class__
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'model': self.model._meta.model_name,
                        'app_label': self.model._meta.app_label,
                        'item': self.item})
        return context


class EditItemView(ConceptEditFormView, UpdateView):
    template_name = "aristotle_mdr/actions/advanced_editor.html"
    permission_required = "aristotle_mdr.user_can_edit"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slots_active = is_active_module('aristotle_mdr.contrib.slots')
        self.identifiers_active = is_active_module('aristotle_mdr.contrib.identifiers')

    def get_form_class(self):
        return MDRForms.wizards.subclassed_edit_modelform(self.model)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'instance': self.item,
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        slot_formset = None
        self.object = self.item

        if form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                item = form.save(commit=False)

                has_change_comments = form.data.get('change_comments', False)
                change_comments = form.data.get('change_comments', "")
                if self.slots_active:
                    slot_formset = self.get_slots_formset()(request.POST, request.FILES, item.concept)
                    if slot_formset.is_valid():

                        # Save the slots
                        slot_formset.save()

                        # Save the change comments
                        if not has_change_comments:
                            change_comments += construct_change_message(request, form, [slot_formset])
                    else:
                        return self.form_invalid(form, slots_FormSet=slot_formset)

                if self.identifiers_active:
                    id_formset = self.get_identifier_formset()(request.POST, request.FILES, item.concept)
                    if id_formset.is_valid():

                        # Save the slots
                        id_formset.save()

                        if not has_change_comments:
                            change_comments += construct_change_message(request, form, [id_formset])
                    else:
                        return self.form_invalid(form, identifier_FormSet=id_formset)

                if (hasattr(self.item, 'serialize_weak_entities')):
                    # if weak formset is active

                    (GenericFormSet, model_to_add_field) = self.get_weak_formset()
                    weak_formset = GenericFormSet(request.POST, request.FILES)

                    if weak_formset.is_valid():

                        one_to_many_formset_save(weak_formset, self.item, 'order', model_to_add_field)

                        if not has_change_comments:
                            change_comments += construct_change_message(request, form, [weak_formset])

                    else:

                        return self.form_invalid(form, identifier_FormSet=weak_formset)


                reversion.revisions.set_user(request.user)
                reversion.revisions.set_comment(change_comments)
                form.save_m2m()
                item.save()
                return HttpResponseRedirect(url_slugify_concept(self.item))

        return self.form_invalid(form)

    def get_slots_formset(self):
        from aristotle_mdr.contrib.slots.forms import slot_inlineformset_factory
        return slot_inlineformset_factory(model=self.model)

    def get_identifier_formset(self):
        from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier

        return inlineformset_factory(
            MDR._concept, ScopedIdentifier,
            can_delete=True,
            fields=('concept', 'namespace', 'identifier', 'version'),
            extra=1,
            )

    def get_weak_formset(self):

        weak = self.item.serialize_weak_entities
        entity = weak[0] #needs to be for loop

        field_model = getattr(self.item, entity[1]).model
        logger.debug(field_model)
        # get the model to add field
        modelname = self.model.__name__.lower()
        model_to_add_field = ''
        for field in field_model._meta.fields:
            # compare field name all lowercase with underscores removed
            if field.name.lower().replace('_', '') == modelname:
                model_to_add_field = field.name

        formset = one_to_many_formset_factory(field_model, model_to_add_field, 'order')

        return (formset, model_to_add_field)


    def form_invalid(self, form, slots_FormSet=None, identifier_FormSet=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form, slots_FormSet=slots_FormSet))

    def get_context_data(self, *args, **kwargs):
        from aristotle_mdr.contrib.slots.models import Slot
        context = super().get_context_data(*args, **kwargs)
        if self.slots_active and kwargs.get('slots_FormSet', None):
            context['slots_FormSet'] = kwargs['slots_FormSet']
        else:
            context['slots_FormSet'] = self.get_slots_formset()(
                queryset=Slot.objects.filter(concept=self.item.id),
                instance=self.item.concept
                )
        from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier
        if self.identifiers_active and kwargs.get('identifier_FormSet', None):
            context['identifier_FormSet'] = kwargs['identifier_FormSet']
        else:
            context['identifier_FormSet'] = self.get_identifier_formset()(
                queryset=ScopedIdentifier.objects.filter(concept=self.item.id),
                instance=self.item.concept
                )

        if (hasattr(self.item, 'serialize_weak_entities')):
            weak = self.item.serialize_weak_entities
            entity = weak[0] #needs to be for loop
            # query weak entity
            queryset = getattr(self.item, entity[1]).all()

            (formset, mtaf) = self.get_weak_formset()

            weak_formset = formset(
                queryset=queryset,
                initial=[{'ORDER': queryset.count() + 1}]
            )

            context['weak_formset'] = weak_formset


        context['show_slots_tab'] = self.slots_active
        context['show_id_tab'] = self.identifiers_active



        return context


class CloneItemView(ConceptEditFormView, DetailView, CreateView):
    template_name = "aristotle_mdr/create/clone_item.html"
    permission_required = "aristotle_mdr.user_can_view"

    def get_form_class(self):
        return MDRForms.wizards.subclassed_clone_modelform(self.model)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'initial': concept_to_clone_dict(self.item)
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                new_clone = form.save(commit=False)
                new_clone.submitter = self.request.user
                new_clone.save()
                reversion.revisions.set_user(self.request.user)
                reversion.revisions.set_comment("Cloned from %s (id: %s)" % (self.item.name, str(self.item.pk)))
                return HttpResponseRedirect(url_slugify_concept(new_clone))
        else:
            return self.form_invalid(form)
