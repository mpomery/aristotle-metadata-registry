from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView, DetailView, UpdateView
)

import reversion

from aristotle_mdr.utils import (
    concept_to_clone_dict,
    construct_change_message, url_slugify_concept, is_active_module,
    get_m2m_through
)
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR

from aristotle_mdr.views.utils import ObjectLevelPermissionRequiredMixin

import logging

from aristotle_mdr.contrib.generic.forms import (
    one_to_many_formset_factory, one_to_many_formset_save,
    one_to_many_formset_excludes, one_to_many_formset_filters,
    through_formset_factory, ordered_formset_save,
    get_weak_formset, get_order_formset
)
import re

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
        through_list = get_m2m_through(self.item)

        if form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                item = form.save(commit=False)

                has_change_comments = form.data.get('change_comments', False)
                change_comments = form.data.get('change_comments', "")
                formset_invalid = False
                changed_formsets = []
                formsets_to_save = []
                if self.slots_active:
                    slot_formset = self.get_slots_formset()(request.POST, request.FILES, item.concept)

                    if not slot_formset.is_valid():
                        formset_invalid = True

                    # Save the slots
                    formsets_to_save.append({
                        'formset': slot_formset,
                        'type': 'slot',
                        'saveargs': None
                    })

                if self.identifiers_active:
                    id_formset = self.get_identifier_formset()(request.POST, request.FILES, item.concept)

                    if not id_formset.is_valid():
                        formset_invalid = True

                    # Save the slots
                    formsets_to_save.append({
                        'formset': id_formset,
                        'type': 'identifiers',
                        'saveargs': None
                    })

                if (hasattr(self.item, 'serialize_weak_entities')):
                    # if weak formset is active
                    weak = self.item.serialize_weak_entities

                    for entity in weak:

                        formset_info = self.get_weak_formset(entity, postdata=request.POST)

                        weak_formset = formset_info['formset']

                        if not weak_formset.is_valid():
                            formset_invalid = True

                        formsets_to_save.append({
                            'formset': weak_formset,
                            'type': 'weak',
                            'saveargs': {
                                'formset': weak_formset,
                                'item': self.item,
                                'model_to_add_field': formset_info['model_field'],
                                'ordering_field': formset_info['ordering']
                            }
                        })

                if through_list:
                    # If there are through formsets
                    for through in through_list:
                        formset = self.get_order_formset(through, request.POST)

                        if not formset.is_valid():
                            formset_invalid = True

                        formsets_to_save.append({
                            'formset': formset,
                            'type': 'through',
                            'saveargs': {
                                'formset': formset,
                                'item': self.item,
                                'model_to_add_field': through['item_fields'][0],
                                'ordering_field': 'order'
                            }
                        })

                if formset_invalid:
                    return self.form_invalid(form, formsets=formsets_to_save)
                else:
                    for formsetinfo in formsets_to_save:
                        if formsetinfo['saveargs']:
                            ordered_formset_save(**formsetinfo['saveargs'])
                        else:
                            formsetinfo['formset'].save()

                    # save the change comments
                    # if not has_change_comments:
                    #     change_comments += construct_change_message(request, form, changed_formsets)

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

    def get_weak_formset(self, entity, postdata=None, queryset=None):
        return get_weak_formset(entity, self.model, item=self.item, postdata=postdata, queryset=queryset)

    def get_order_formset(self, through, postdata=None):
        return get_order_formset(through, self.item, postdata)

    def form_invalid(self, form, formsets=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        error_formsets = {}
        for formsetinfo in formsets:
            type = formsetinfo['type']
            if type == 'identifiers':
                error_formsets['identifier_FormSet'] = formsetinfo['formset']
            elif type == 'slot':
                error_formsets['slots_FormSet'] = formsetinfo['formset']
            elif type == 'weak':
                if 'weak_formsets' not in error_formsets.keys():
                    error_formsets['weak_formsets'] = []
                error_formsets['weak_formsets'].append({'formset': formsetinfo['formset']})
            elif type == 'through':
                if 'through_formsets' not in error_formsets.keys():
                    error_formsets['through_formsets'] = []
                error_formsets['through_formsets'].append({'formset': formsetinfo['formset']})

        logger.debug('error formsets are {}'.format(error_formsets))

        return self.render_to_response(self.get_context_data(form=form, error_formsets=error_formsets))

    def get_context_data(self, *args, **kwargs):
        from aristotle_mdr.contrib.slots.models import Slot
        context = super().get_context_data(*args, **kwargs)

        if 'error_formsets' in kwargs:
            context.update(kwargs['error_formsets'])
            return context

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
            formsets = []
            for entity in weak:
                # query weak entity
                queryset = getattr(self.item, entity[1]).all()

                weak_formset = self.get_weak_formset(entity, queryset=queryset)['formset']
                weak_formset = one_to_many_formset_filters(weak_formset, self.item)

                title = 'Edit ' + queryset.model.__name__
                # add spaces before capital letters
                title = re.sub(r"\B([A-Z])", r" \1", title)

                formsets.append({'formset': weak_formset, 'title': title})

            context['weak_formsets'] = formsets

        context['show_slots_tab'] = self.slots_active
        context['show_id_tab'] = self.identifiers_active

        through_list = get_m2m_through(self.item)
        through_formsets = []
        for through in through_list:
            formset = self.get_order_formset(through)
            through_formsets.append({'formset': formset, 'title': through['field_name'].title()})

        context['through_formsets'] = through_formsets

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
